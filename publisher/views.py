# -*- encoding: utf-8 -*-

import os
import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.forms.util import ErrorList
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import simplejson

from private_files.views import get_file as private_files_get_file

from common.modules import get_publication_module, has_module
from common.permissions import can
from common.shortcuts import response_json, response_json_error

from publisher import functions as publisher_functions

from exceptions import *
from forms import *
from models import *

from accounts.forms import EmailAuthenticationForm
from accounts.models import UserPublisher, UserPublisherInvitation

# Publisher Dashboard ######################################################################

@login_required
def view_dashboard(request):
    try:
        user_publisher = UserPublisher.objects.get(user=request.user, is_default=True)
        return redirect('view_publisher_dashboard', publisher_id=user_publisher.publisher.id)
    except UserPublisher.DoesNotExist:
        if UserPublisher.objects.filter(user=request.user).count() == 0:
            return redirect('view_user_welcome')
        else:
            # If a user does not set any default publisher, pick the first one
            user_publisher = UserPublisher.objects.filter(user=request.user).order_by('created')[0]
            return redirect('view_publisher_dashboard', publisher_id=user_publisher.publisher.id)

@login_required
def view_publisher_dashboard(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if request.user.get_profile().is_first_time:
        request.user.get_profile().is_first_time = False
        request.user.get_profile().save()
        first_time = True
    else:
        first_time = False
    
    if not can(request.user, 'view', publisher):
        raise Http404
        
    if can(request.user, 'edit', publisher):
        recent_publications = Publication.objects.filter(publisher=publisher).order_by('-uploaded')
    else:
        recent_publications = Publication.objects.filter(publisher=publisher, status=Publication.STATUS['PUBLISHED']).order_by('-uploaded')
    
    return render(request, 'publisher/dashboard.html', {'publisher':publisher, 'recent_publications':recent_publications, 'first_time':first_time})

# Publication ######################################################################

@login_required
def upload_publication(request, publisher_id, module_name=''):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not can(request.user, 'edit', publisher):
        raise Http404

    if request.method == 'POST':
        if not module_name:
            module_name = request.POST.get('module')
        
        module = get_object_or_404(Module, module_name=module_name)

        if not has_module(publisher, module):
            raise Http404
        
        form = module.get_module_object('forms').UploadPublicationForm(request.POST, request.FILES, publisher=publisher)

        if form.is_valid():
            module_input = form.cleaned_data['module']
            publication = form.cleaned_data['publication']

            if not form.valid_file_type():
                return response_json_error('file-type-invalid')

            publication = publisher_functions.upload_publication(request, module_input, publication, publisher)

            if not publication:
                return response_json_error('upload')
            
            form.after_upload(request, publication)
            
            return response_json({'next_url':reverse('finishing_upload_publication', args=[publication.id])})

        else:
            return response_json_error('form-input-invalid')
    
    else:
        raise Http404

@login_required
def get_upload_progress(request):
    # Return JSON object with information about the progress of an upload.
    progress_id = ''
    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']
    if progress_id:
        from django.utils import simplejson
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        data = cache.get(cache_key)
        return HttpResponse(simplejson.dumps(data))
    else:
        return HttpResponseServerError('Server Error: You must provide X-Progress-ID header or query param.')

@login_required
def finishing_upload_publication(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404
    
    views_module = get_publication_module(publication.publication_type, 'views')
    
    if publication.status != Publication.STATUS['UPLOADED']:
        return redirect('view_publication', publication_id=publication.id)
    
    return views_module.finishing_upload_publication(request, publisher, publication)

@login_required
def cancel_upload_publication(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404
    
    if publication.status != Publication.STATUS['UPLOADED']:
        raise Http404
    
    if request.method == 'POST':
        if 'submit-delete' in request.POST:
            views_module = get_publication_module(publication.publication_type, 'views')
            response = views_module.cancel_upload_publication(request, publisher, publication)
            
            publisher_functions.delete_publication(publication)
            messages.success(request, u'ยกเลิกการอัพโหลดไฟล์เรียบร้อย')
            return response

        else:
            return redirect('finishing_upload_publication', publication_id=publication.id)
    
    return render(request, 'publisher/publication_upload_cancel.html', {'publisher':publisher, 'publication':publication})

@login_required
def view_publication(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'view', publisher):
        raise Http404
    
    if not can(request.user, 'edit', publisher) and publication.status != Publication.STATUS['PUBLISHED']:
        raise Http404
    
    if publication.status == Publication.STATUS['UPLOADED']:
        return redirect('finishing_upload_publication', publication_id=publication.id)
    
    return render(request, 'publisher/%s/publication.html' % publication.publication_type, {'publisher':publisher, 'publication':publication})

@login_required
def download_publication(request, publication_id):
    
    return HttpResponse(publication_id)

@login_required
def get_publication(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)

    if not can(request.user, 'edit', publisher) and publication.status != Publication.STATUS['PUBLISHED']:
        raise Http404
    
    return private_files_get_file(request, 'publication', 'Publication', 'uploaded_file', str(publication.id), 'sample.pdf')

@login_required
def edit_publication(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404
    
    if publication.status == Publication.STATUS['UPLOADED']:
        raise Http404
    
    views_module = get_publication_module(publication.publication_type, 'views')
    return views_module.edit_publication(request, publisher, publication)

@login_required
def edit_publication_status(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404
    
    if publication.status == Publication.STATUS['UPLOADED']:
        raise Http404
    
    if request.method == 'POST':
        form = EditPublicationStatusForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            schedule_date = form.cleaned_data['schedule_date']
            schedule_time = form.cleaned_data['schedule_time']

            if status == 'unpublish':
                publisher_functions.set_publication_unpublished(request, publication)
            
            elif status == 'schedule':
                schedule = datetime.datetime.combine(schedule_date, schedule_time)
                publisher_functions.set_publication_scheduled(request, publication, schedule)
            
            elif status == 'publish':
                publisher_functions.set_publication_published(request, publication)
            
            messages.success(request, u'เปลี่ยนสถานะไฟล์เรียบร้อย')
            return redirect('view_publication', publication.id)

    else:
        # PROCESSING -> 'unpublish', show processing note
        # UNPUBLISHED -> 'unpublish'
        # SCHEDULED -> 'schedule'
        # PROCESSING with SCHEDULED -> 'schedule', show processing note
        # PUBLISHED -> 'publish'
        # PUBLISH WHEN READY -> 'unpublish', show processing note, show publish when ready note

        schedule_date = publication.web_scheduled.date() if publication.web_scheduled else None
        schedule_time = publication.web_scheduled.time() if publication.web_scheduled else None

        is_publish_when_ready = False
        
        if publication.status == Publication.STATUS['UNPUBLISHED']:
            status = 'unpublish'
            is_publish_when_ready = PublicationNotice.objects.filter(publication=publication, notice=PublicationNotice.NOTICE['PUBLISH_WHEN_READY']).exists()
        
        elif publication.status == Publication.STATUS['SCHEDULED']:
            status = 'schedule'

        elif publication.status == Publication.STATUS['PUBLISHED']:
            status = 'publish'

        else:
            status = ''
        
        form = EditPublicationStatusForm(initial={'status':status, 'schedule_date':schedule_date, 'schedule_time':schedule_time})

    return render(request, 'publisher/%s/publication_edit_status.html' % publication.publication_type, {'publisher':publisher, 'publication':publication, 'form':form})

@login_required
def replace_publication(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404
    
    if publication.status == Publication.STATUS['UPLOADED']:
        raise Http404
    
    return render(request, 'publisher/publication_replace.html', {'publisher':publisher, 'publication':publication})

@login_required
def delete_publication(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404
    
    if request.method == 'POST':
        deleted = 'submit-delete' in request.POST

        if deleted:
            views_module = get_publication_module(publication.publication_type, 'views')
            response = views_module.delete_publication(request, deleted, publisher, publication)

            publisher_functions.delete_publication(publication)
        
            messages.success(request, u'ลบไฟล์เรียบร้อย')
            return response

        else:
            return redirect('view_publication', publication_id=publication.id)
    
    return render(request, 'publisher/%s/publication_delete.html' % publication.publication_type, {'publisher':publisher, 'publication':publication})

@login_required
def set_publication_published(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404

    if request.method == 'POST' and request.is_ajax():
        if publication.status == Publication.STATUS['UPLOADED']:
            return response_json_error('invalid-status')
        
        if publication.status == Publication.STATUS['PUBLISHED']:
            return response_json_error('published')
        
        publisher_functions.set_publication_published(request, publication)

        return response_json()
    else:
        raise Http404

@login_required
def set_publication_schedule(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404

    if request.method == 'POST' and request.is_ajax():
        if publication.status == Publication.STATUS['UPLOADED']:
            return response_json_error('invalid-status')
        
        try:
            (s_year, s_month, s_day) = request.POST.get('schedule_date').split('-')
            (s_year, s_month, s_day) = (int(s_year), int(s_month), int(s_day))
            (s_hour, s_minute) = request.POST.get('schedule_time').split(':')
            (s_hour, s_minute) = (int(s_hour), int(s_minute))

            schedule = datetime.datetime(s_year, s_month, s_day, s_hour, s_minute, 0)

        except:
            return response_json_error('invalid-schedule')
        
        if schedule <= datetime.datetime.today():
            return response_json_error('past')
        
        publisher_functions.set_publication_scheduled(request, publication, schedule)
        
        return response_json()
    else:
        raise Http404

@login_required
def set_publication_cancel_schedule(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404

    if request.method == 'POST' and request.is_ajax():
        if not publication.status in (Publication.STATUS['UNPUBLISHED'], Publication.STATUS['PUBLISHED']):
            return response_json_error('invalid-status')
        
        publisher_functions.set_publication_scheduled_cancel(request, publication)
        
        return response_json()
    else:
        raise Http404
