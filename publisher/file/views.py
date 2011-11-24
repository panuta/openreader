# -*- encoding: utf-8 -*-

import os
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import simplejson

from common.modules import has_module
from common.permissions import can

from publisher import functions as publisher_functions
from publisher.models import Publisher, Publication

from forms import *
from models import *

# PUBLICATION ################################################################################

def finishing_upload_publication(request, publisher, publication):
    if request.method == 'POST':
        form = FinishUploadFileForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']

            publish_status = int(form.cleaned_data['publish_status']) if form.cleaned_data['publish_status'] else None
            schedule_date = form.cleaned_data['schedule_date']
            schedule_time = form.cleaned_data['schedule_time']

            publication = publisher_functions.finishing_upload_publication(request, publication, title, description, publish_status, schedule_date, schedule_time)

            messages.success(request, 'บันทึกข้อมูลเรียบร้อย')

            return redirect('view_files', publisher_id=publisher.id)
            
    else:
        form = FinishUploadFileForm()
    
    return render(request, 'publisher/file/publication_finishing.html', {'publisher':publisher, 'publication':publication, 'form':form})

def cancel_upload_publication(request, publisher, publication):
    # MESSAGE
    return redirect('view_files', publisher_id=publisher.id)

def view_publication(request, publisher, publication):

    return render(request, 'publisher/file/publication.html', {'publisher':publisher, 'publication':publication})

def edit_publication(request, publisher, publication):
    if request.method == 'POST':
        form = EditFileDetailsForm(request.POST)
        if form.is_valid():
            publication.title = form.cleaned_data['title']
            publication.description = form.cleaned_data['description']
            publication.save()
            
            # MESSAGE

            return redirect('view_publication', publication.id)
    else:
        form = EditFileDetailsForm(initial={'title':publication.title, 'description':publication.description})

    return render(request, 'publisher/file/publication_edit.html', {'publisher':publisher, 'publication':publication, 'form':form})

def edit_publication_status(request, publisher, publication):
    if request.method == 'POST':
        form = EditFileStatusForm(request.POST)
        if form.is_valid():
            publish_status = int(form.cleaned_data['publish_status']) if form.cleaned_data['publish_status'] else None
            schedule_date = form.cleaned_data['schedule_date']
            schedule_time = form.cleaned_data['schedule_time']

            publication.publish_status = publish_status

            if publish_status == Publication.PUBLISH_STATUS['UNPUBLISHED']:
                publication.publish_schedule = None
                publication.published = None
                publication.published_by = None

            elif publish_status == Publication.PUBLISH_STATUS['SCHEDULED']:
                publication.publish_schedule = datetime.datetime(schedule_date.year, schedule_date.month, schedule_date.day, schedule_time.hour, schedule_time.minute)
                publication.published = None
                publication.published_by = request.user

            elif publish_status == Publication.PUBLISH_STATUS['PUBLISHED']:
                publication.publish_schedule = None
                publication.published = datetime.datetime.today()
                publication.published_by = request.user
            
            publication.save()

            # MESSAGE

            return redirect('view_publication', publication.id)
    else:
        schedule_date = publication.publish_schedule.date() if publication.publish_schedule else None
        schedule_time = publication.publish_schedule.time() if publication.publish_schedule else None
        form = EditFileStatusForm(initial={'publish_status':str(publication.publish_status), 'schedule_date':schedule_date, 'schedule_time':schedule_time})
    
    return render(request, 'publisher/file/publication_edit_status.html', {'publisher':publisher, 'publication':publication, 'form':form})

def delete_publication(request, deleted, publisher, publication):
    if deleted:
        # MESSAGE
        return redirect('view_files', publisher_id=publisher.id)
        
    else:
        return redirect('view_publication', publication_id=publication.id)

def gather_publisher_statistics(request, publisher):
    return {
        'published_files_count': Publication.objects.filter(publisher=publisher, publication_type='file', publish_status=Publication.PUBLISH_STATUS['PUBLISHED']).count()
    }

# FILE PUBLICATION ################################################################################

@login_required
def view_files(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not has_module(publisher, 'file') or not can(request.user, 'view', publisher):
        raise Http404

    files = Publication.objects.filter(publisher=publisher, publication_type='file').order_by('uploaded')

    return render(request, 'publisher/file/files.html', {'publisher':publisher, 'files':files})

@login_required
def view_files_by_shelf(request, publisher_id, shelf_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    shelf = get_object_or_404(Shelf, pk=shelf_id)

    if shelf.publisher.id == publisher.id or not has_module(publisher, 'shelf') or not can(request.user, 'view', publisher):
        raise Http404
    
    files = []
    for item in PublicationShelf.objects.filter(shelf=shelf, publication__publication_type='file').order_by('publication__uploaded'):
        files.append(item.publication)
    
    return render(request, 'publisher/file/files.html', {'publisher':publisher, 'files':files, 'shelf':shelf})
