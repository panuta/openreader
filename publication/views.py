# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import simplejson

from common.permissions import can
from common.shortcuts import response_json, response_json_success, response_json_error
from common.utilities import format_abbr_datetime

from publication import functions as publication_functions

from forms import *
from models import *

@login_required
def publish_publication(request):
    if request.method == 'POST' and request.is_ajax():
        publication_uid = request.POST.get('uid')

        if not publication_uid:
            return response_json_error('missing-parameters')
        
        publication = get_object_or_404(Publication, uid=publication_uid)
        organization = publication.organization

        if not can(request.user, 'edit', organization):
            return response_json_error('access-denied')
    
        if publication.status == Publication.STATUS['PUBLISHED']:
            return response_json_error('invalid-status')
        
        publication_functions.publish_publication(request, publication)

        if publication.is_processing:
            return response_json({'status':'success', 'error':'processing'})

        return response_json_success({'published':format_abbr_datetime(publication.published)})
    
    raise Http404

@login_required
def unpublish_publication(request):
    if request.method == 'POST' and request.is_ajax():
        publication_uid = request.POST.get('uid')

        if not publication_uid:
            return response_json_error('missing-parameters')
        
        publication = get_object_or_404(Publication, uid=publication_uid)
        organization = publication.organization

        if not can(request.user, 'edit', organization):
            return response_json_error('access-denied')
    
        if publication.status == Publication.STATUS['UNPUBLISHED']:
            if not publication.is_processing and not publication.status != Publication.STATUS['UNPUBLISHED']:
                return response_json_error('invalid-status')
        
        publication_functions.unpublish_publication(request, publication)

        if publication.is_processing:
            return response_json({'status':'success', 'error':'processing'})

        return response_json_success()
    
    raise Http404