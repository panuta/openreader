# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseServerError, Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from private_files.views import get_file as private_files_get_file

from common.permissions import can
from common.shortcuts import response_json, response_json_success, response_json_error
from common.utilities import format_abbr_datetime

from publication import functions as publication_functions

from models import Publication

@login_required
def download_publication(request, publication):
    if not can(request.user, 'view', {'organization':publication.organization}):
        raise Http404
    
    return private_files_get_file(request, 'publication', 'Publication', 'uploaded_file', str(publication.id), '%s.%s' % (publication.original_file_name, publication.file_ext))

@login_required
def publish_publication(request):
    if request.method == 'POST' and request.is_ajax():
        publication_uid = request.POST.get('uid')

        if not publication_uid:
            return response_json_error('missing-parameters')
        
        publication = get_object_or_404(Publication, uid=publication_uid)
        organization = publication.organization

        if not can(request.user, 'edit', {'organization':organization}):
            return response_json_error('access-denied')
    
        if publication.status in (Publication.STATUS['UNFINISHED'], Publication.STATUS['PUBLISHED']):
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

        if not can(request.user, 'edit', {'organization':organization}):
            return response_json_error('access-denied')
    
        if publication.status in (Publication.STATUS['UNFINISHED'], Publication.STATUS['UNPUBLISHED']):
            if not publication.is_processing and not publication.status != Publication.STATUS['UNPUBLISHED']:
                return response_json_error('invalid-status')
        
        publication_functions.unpublish_publication(request, publication)

        if publication.is_processing:
            return response_json({'status':'success', 'error':'processing'})

        return response_json_success()
    
    raise Http404