from django.utils import simplejson

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render

from publisher.models import *

def request_access(request):
    if request.method == 'GET':
        email = request.GET.get('email', '')
        password = request.GET.get('password', '')
        device_id = request.GET.get('device_id', '')
        app_secret = request.GET.get('app_secret', '')
        app_id = request.GET.get('app_id', '')

        if email and password and device_id and app_secret:

            # Check app secret

            # Check email + password

            # Check device id

            # Check access

            # Generate access token

            return HttpResponse('this_is_your_token')

        else:
            return HttpResponse('missing parameters')

    else:
        raise Http404

def request_download(request):
    if request.method == 'GET':
        device_id = request.GET.get('device_id', '')
        app_secret = request.GET.get('app_secret', '')
        app_id = request.GET.get('app_id', '')

        access_token = request.GET.get('access_token', '')
        publication_id = request.GET.get('publication_id', '')

        if device_id and app_secret and access_token and publication_id:

            # Check app secret

            # Check access token and device id

            # Processing publication

            # Return publication unlock key

            return HttpResponse('use_this_to_unlock')

        else:
            return HttpResponse('missing parameters')
    else:
        raise Http404

"""
Parameters
'shelf'
'type'
'sort'
'publisher'
'limit'
"""
def list_publication(request):
    if request.method == 'GET':
        if 'publisher' not in request.GET or 'type' not in request.GET:
            raise Http404
        
        publisher = request.GET.get('publisher')
        shelf = request.GET.get('shelf')
        publication_type = request.GET.get('type')
        sort = request.GET.get('sort')
        limit = request.GET.get('limit')
        
        publisher = get_object_or_404(Publisher, pk=publisher)

        if publication_type not in ('book', 'magazine', 'file'):
            raise Http404
        
        objects = Publication.objects.filter(publisher=publisher, publication_type=publication_type)

        if shelf:
            shelf = get_object_or_404(PublisherShelf, pk=shelf)
            objects.filter(shelves__in=[shelf])
        
        if sort and sort in ('uploaded', '-uploaded'):
            objects.order_by(sort)
        
        result = []
        for publication in objects:
            result.append({'uid':publication.uid, 'title':publication.title, })
        
        return HttpResponse(simplejson.dumps(result))
        
    else:
        raise Http404



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

