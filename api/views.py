from httpauth import logged_in_or_basicauth
from datetime import datetime, timedelta
import md5
import base64
from StringIO import StringIO

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.core import serializers
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_GET
from django.utils import simplejson

from common.fileservers import generate_download_url

from accounts.permissions import get_backend as get_permission_backend
from models import *
from domain.models import *


def _has_required_parameters(request, names):
    if request.method != 'GET':
        raise Http404
        
    for name in names:
        if name not in request.GET:
            raise Http404
    return True
    
def _get_email(request):
    # TODO: check if use token, return email from database
    
    auth = request.META['HTTP_AUTHORIZATION'].split()
    email, password = base64.b64decode(auth[1]).split(':')
    return email
    
@logged_in_or_basicauth()
def request_access(request):
    #http://staff%40openreader.com:panuta@localhost:8000/api/request/access/
    email = _get_email(request)
    
    t = datetime.now()
    token = md5.md5(email + t.strftime('%s') + str(t.microsecond)).hexdigest()
    expired = datetime.now() + timedelta(days=1)
    Token.objects.filter(email=email).delete()
    Token.objects.create(email=email, token=token, expired=expired)
        
    return HttpResponse(simplejson.dumps({'token': token}))

@logged_in_or_basicauth()
def list_publication(request):
    #http://admin%40openreader.com:panuta@localhost:8000/api/list/publication/?organization=opendream
    if _has_required_parameters(request, ['organization']):
        result = {}
        
        email = _get_email(request)
        organization = request.GET.get('organization')
        
        user_profile = UserProfile.objects.get(user__email=email)
        
        try:
            user_organization = UserOrganization.objects.get(organization__slug=organization, user=user_profile.user)
        except:
            raise Http404
        
        result['user_profile'] = model_to_dict(user_profile)
        result['organization'] = model_to_dict(user_organization.organization)
        
        shelves = get_permission_backend(request).get_viewable_shelves(user_profile.user, user_organization.organization)
        # shelves = user_profile.get_viewable_shelves(user_organization.organization)
        shelves_list = []
        for shelf in shelves:
            shelf_dict = model_to_dict(shelf)
            shelf_dict['archive'] = UserShelfArchive.objects.is_archive(user_profile.user, shelf)
            shelf_dict['publications'] = []
            for publication in shelf.publication_set.all():
                publication_dict = model_to_dict(publication)
                
                publication_dict['auto_sync'] =  shelf.auto_sync
                publication_dict['tags'] = [tag.tag_name for tag in publication.tags.all()]
                
                url = reverse('download_publication', args=[publication.uid])
                url = request.build_absolute_uri(url)
                publication_dict['url'] = url
                
                publication_dict['large_thumbnail'] = request.build_absolute_uri(publication.get_large_thumbnail())
                publication_dict['small_thumbnail'] = request.build_absolute_uri(publication.get_small_thumbnail())
                
                publication_dict['uploaded'] = publication.uploaded.strftime("%Y-%m-%d %H:%M:%S")
                publication_dict['modified'] = publication.modified.strftime("%Y-%m-%d %H:%M:%S")
                
                publication_dict['filesize'] = publication.uploaded_file.size
                
                del(publication_dict['uploaded_file'])
                shelf_dict['publications'].append(publication_dict)
                
            shelves_list.append(shelf_dict)
        
        result['shelves'] = shelves_list
    
    return HttpResponse(simplejson.dumps(result))

@logged_in_or_basicauth()
def get_user_organization(request):
    #http://admin@openreader.com:panuta@10.0.1.14:8000/api/get/userorganization/
    email = _get_email(request)
    user_profile = UserProfile.objects.get(user__email=email)
    user = user_profile.user
    user_organization = UserOrganization.objects.filter(user=user)
    
    result = {}
    result['user_profile'] = model_to_dict(user_profile)
    result['user_profile']['fullname'] = user_profile.get_fullname()
    
    result['organizations'] = []
    
    for item in user_organization:
        data = model_to_dict(item.organization)
        result['organizations'].append(data)
    
    return HttpResponse(simplejson.dumps(result))

from django.utils.importlib import import_module

def _extract_user(request):
    if request.user.is_authenticated():
        return request.user
    else:
        try:
            auth = request.META['HTTP_AUTHORIZATION'].split(' ')
            email, password = base64.b64decode(auth[1]).split(':')
            return UserProfile.get_instance_from_email(email).user
        except:
            return None

@require_GET
@logged_in_or_basicauth()
def request_download_publication(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)
    user = _extract_user(request)

    # if not can(user, 'view_publication', publication.organization, {'publication':publication}):
    if not get_permission_backend(request).get_publication_access(user, publication):
        raise Http403
    
    server_urls = []
    for server in OrganizationDownloadServer.objects.filter(organization=publication.organization).order_by('-priority'):
        download_url = generate_download_url(server, publication)
        if download_url:
            server_urls.append(download_url)
    
    return HttpResponse(simplejson.dumps(server_urls))

@require_GET
@logged_in_or_basicauth()
def user_archive_shelves(request):
    if _has_required_parameters(request, ['shelves']):
        str_shelves = request.GET.get('shelves')
        shelves = simplejson.load(StringIO(str_shelves))
        for s in shelves:
            try:
                shelf = OrganizationShelf.objects.get(id=s['id'])
            except OrganizationShelf.DoesNotExist:
                return HttpResponse('Fail, shelf[%s] does not exist.' % s['id'])

            if s['archive']:
                archive, created = UserShelfArchive.objects.get_or_create(user=request.user, shelf=shelf)
            else:
                UserShelfArchive.objects.filter(user=request.user, shelf=shelf).delete()
                
    return HttpResponse('Success')
