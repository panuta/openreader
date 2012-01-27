from django.utils import simplejson

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.core import serializers
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse


from publisher.models import *
from api.models import *
from accounts.models import UserOrganization
from document.models import *

from httpauth import logged_in_or_basicauth

from datetime import datetime, timedelta
import md5
import base64

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
        
        shelves = user_profile.get_viewable_shelves(user_organization.organization)
        shelves_list = []
        for shelf in shelves:
            shelf_dict = model_to_dict(shelf)
            shelf_dict['icon'] = ''
            shelf_dict['publications'] = []
            for publication in shelf.publication_set.all():
                publication_dict = model_to_dict(publication)
                
                publication_dict['auto_sync'] =  shelf.auto_sync
                
                url = reverse('download_publication', args=[publication.uid])
                url = request.build_absolute_uri(url)
                publication_dict['url'] = url
                
                publication_dict['large_thumbnail'] = request.build_absolute_uri(publication.get_large_thumbnail())
                publication_dict['small_thumbnail'] = request.build_absolute_uri(publication.get_small_thumbnail())
                
                publication_dict['uploaded'] = publication.uploaded.strftime("%Y-%m-%d %H:%M:%S")
                publication_dict['modified'] = publication.modified.strftime("%Y-%m-%d %H:%M:%S")
                
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


# ===============
# Old code
# ===============
def get_publication(request):
    if request.method == 'GET':
        publication = request.GET.get('publication')

        publication = get_object_or_404(Publication, uid=publication)

        result = {'uid':publication.uid, 'title':publication.title, 'description':publication.description}
        return HttpResponse(simplejson.dumps(result))

    else:
        raise Http404



def search_publication(request):
    if request.method == 'GET':
        title = request.GET.get('title')

        search_result = None

        if title:
            search_result = Publication.objects.filter(title__icontains=title)
        
        if search_result:
            result = []
            for publication in search_result:
                result.append({'uid':publication.uid, 'title':publication.title, })
            return HttpResponse(simplejson.dumps(result))
        
        else:
            return HttpResponse('')
        
    else:
        raise Http404



def list_shelf(request):
    if request.method == 'GET':
        publisher = request.GET.get('publisher')

        publisher = get_object_or_404(Publisher, pk=publisher)

        shelves = PublisherShelf.objects.filter(publisher=publisher).order_by('name')

        result = []
        for shelf in shelves:
            result.append({'id':shelf.id, 'name':shelf.name})
        
        return HttpResponse(simplejson.dumps(result))

    else:
        raise Http404





def get_publication_new_release(request):
    if request.method == 'GET':
        pass
    else:
        raise Http404

def get_publication_top_charts(request):
    if request.method == 'GET':
        pass
    else:
        raise Http404

def get_publication_categories(request):
    if request.method == 'GET':
        pass
    else:
        raise Http404

def get_publication_list(request):
    if request.method == 'GET':
        pass
    else:
        raise Http404

def get_publication_covers(request):
    if request.method == 'GET':
        pass
    else:
        raise Http404

def get_publication_details(request):
    if request.method == 'GET':
        pass
    else:
        raise Http404

def search_publication(request):
    if request.method == 'GET':
        pass
    else:
        raise Http404

def get_accounts_purchase_history(request):
    if request.method == 'GET':
        pass
    else:
        raise Http404

