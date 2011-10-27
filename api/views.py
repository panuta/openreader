from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render

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

