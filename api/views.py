from httpauth import logged_in_or_basicauth
from datetime import datetime, timedelta
import md5
import base64
from StringIO import StringIO

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import redirect, render
from django.core import serializers
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_GET
from django.utils import simplejson
from django.utils.importlib import import_module

from private_files.views import get_file as private_files_get_file
from common.fileservers import generate_download_url

from accounts.permissions import get_backend as get_permission_backend
from models import *
from domain.models import *


def _has_required_parameters(request, names):
    if request.method != 'GET':
        return HttpResponse('Wrong method', status=404)
        
    for name in names:
        if name not in request.GET:
            return HttpResponse('Page not found', status=404)
    return True
    
def _get_email(request):
    # TODO: check if use token, return email from database
    
    auth = request.META['HTTP_AUTHORIZATION'].split()
    email, password = base64.b64decode(auth[1]).split(':')
    return email

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
            return HttpResponse('Page not found', status=404)

        if not user_organization.is_active:
            return HttpResponse('No permissions', status=403)
        
        result['user_profile'] = model_to_dict(user_profile)
        result['organization'] = model_to_dict(user_organization.organization)
        
        shelves = get_permission_backend(request).get_viewable_shelves(user_profile.user, user_organization.organization)
        # shelves = user_profile.get_viewable_shelves(user_organization.organization)
        shelves_list = []
        for shelf in shelves:
            shelf_dict = model_to_dict(shelf)
            shelf_dict['archive'] = OrganizationShelf.objects.is_archive(user_profile.user, shelf)
            shelf_dict['publications'] = []
            for publication in shelf.publication_set.all():
                publication_dict = model_to_dict(publication)
                
                publication_dict['auto_sync'] =  shelf.auto_sync
                publication_dict['tags'] = [tag.tag_name for tag in publication.tags.all()]
                
                url = reverse('api_request_download_publication', args=[publication.uid])
                url = request.build_absolute_uri(url)
                publication_dict['url'] = url
                
                publication_dict['large_thumbnail'] = request.build_absolute_uri(publication.get_large_thumbnail())
                publication_dict['small_thumbnail'] = request.build_absolute_uri(publication.get_small_thumbnail())
                
                if publication.uploaded:
                    publication_dict['uploaded'] = publication.uploaded.strftime("%Y-%m-%d %H:%M:%S")
                if publication.modified:
                    publication_dict['modified'] = publication.modified.strftime("%Y-%m-%d %H:%M:%S")
                if publication.replaced:
                    publication_dict['replaced'] = publication.replaced.strftime("%Y-%m-%d %H:%M:%S")
                
                publication_dict['filesize'] = publication.uploaded_file.size
                
                del(publication_dict['uploaded_file'])
                shelf_dict['publications'].append(publication_dict)
                
            shelves_list.append(shelf_dict)
        
        result['shelves'] = shelves_list
    
    return HttpResponse(simplejson.dumps(result))

@logged_in_or_basicauth()
def list_user_organization(request):
    #http://admin@openreader.com:panuta@10.0.1.14:8000/api/get/userorganization/
    email = _get_email(request)
    user_profile = UserProfile.objects.get(user__email=email)
    user = user_profile.user
    user_organization = UserOrganization.objects.filter(user=user, is_active=True)
    
    result = {}
    result['user_profile'] = model_to_dict(user_profile)
    result['user_profile']['fullname'] = user_profile.get_fullname()
    
    result['organizations'] = []
    
    for item in user_organization:
        data = model_to_dict(item.organization)
        result['organizations'].append(data)
    
    return HttpResponse(simplejson.dumps(result))

@require_GET
@logged_in_or_basicauth()
def request_download_publication(request, publication_uid):
    try:
        publication = Publication.objects.get(uid=publication_uid)
    except Publication.DoesNotExists:
        return HttpResponse('Page not found', status=404)

    user = _extract_user(request)

    try:
        user_organization = UserOrganization.objects.get(organization=publication.organization, user=user, is_active=True)
    except:
        return HttpResponse('No permissions', status=403)

    if not get_permission_backend(request).get_publication_access(user, publication):
        return HttpResponse('No permissions', status=403)

    # ----- CDN support is not available for NBTC -----
    # server_urls = []
    # for server in OrganizationDownloadServer.objects.filter(organization=publication.organization).order_by('-priority'):
    #     download_url = generate_download_url(server, publication)
    #     if download_url:
    #         server_urls.append(download_url)
    # return HttpResponse(simplejson.dumps(server_urls))

    return private_files_get_file(request, 'domain', 'Publication', 'uploaded_file', str(publication.id), '%s.%s' % (publication.original_file_name, publication.file_ext))

@logged_in_or_basicauth()
def user_config_shelves(request):

    if 'archive_shelves' in request.REQUEST:
        params = request.REQUEST.get('archive_shelves')
        shelf_ids = params.split('|')
        OrganizationShelf.objects.archive(user=request.user, shelf_ids=shelf_ids)

    if 'unarchive_shelves' in request.REQUEST:
        params = request.REQUEST.get('unarchive_shelves')
        shelf_ids = params.split('|')
        OrganizationShelf.objects.unarchive(user=request.user, shelf_ids=shelf_ids)

    return HttpResponse('Success')


@logged_in_or_basicauth()
def api_request_secret_key(request):
    email = _get_email(request)
    user_profile = UserProfile.objects.get(user__email=email)

    result = {}
    result['user_profile'] = model_to_dict(user_profile)

    from Crypto.Cipher import AES
    SECRET_KEY = 'STOPCUTTINGTREESAVETHEWORLDWORLD'
    IV_KEY = 'DJANGO14ISBETTER'
    obj = AES.new(SECRET_KEY, AES.MODE_CBC, IV_KEY)
    message = user_profile.user.username
    while len(message) < 16:
        message += message
    message = message[:16]
    ciphertext = obj.encrypt(message)

    result['key'] = unicode(ciphertext, 'utf-16')

    return HttpResponse(simplejson.dumps(result))
