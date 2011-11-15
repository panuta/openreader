import os
import datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import simplejson

from common.permissions import can

from publication import functions as publication_functions
from publication.models import *

from publication.magazine import MODULE_CODE
#from exceptions import *
from forms import *
from models import *

# FROM PUBLICATION ################################################################################

def finishing_upload_publication(request, publisher, uploading_publication):
    if request.method == 'POST':
        form = FinishUploadMagazineIssueForm(request.POST, publisher=publisher, uploading_publication=uploading_publication)
        if form.is_valid():
            magazine = form.cleaned_data['magazine']
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            publish_status = int(form.cleaned_data['publish_status']) if form.cleaned_data['publish_status'] else None
            schedule_date = form.cleaned_data['schedule_date']
            schedule_time = form.cleaned_data['schedule_time']

            publication = publication_functions.finishing_upload_publication(request, publisher, uploading_publication, title, description, publish_status, schedule_date, schedule_time)

            if uploading_publication.parent_id:
                magazine = Magazine.objects.get(id=uploading_publication.parent_id)
            MagazineIssue.objects.create(publication=publication, magazine=magazine)

            return redirect('view_publication', publication_id=publication.id)

    else:
        form = FinishUploadMagazineIssueForm(publisher=publisher, uploading_publication=uploading_publication)
    
    return render(request, 'publication/magazine/publication_finishing.html', {'publisher':publisher, 'uploading_publication':uploading_publication, 'form':form})

def view_publication(request, publisher, publication):

    return render(request, 'publication/magazine/publication.html', {'publisher':publisher, 'publication':publication})

def edit_publication(request, publisher, publication):
    if request.method == 'POST':
        form = MagazineIssueForm(request.POST)
        if form.is_valid():
            publication.title = form.cleaned_data['title']
            publication.description = form.cleaned_data['description']
            
            publish_status = int(form.cleaned_data['publish_status']) if form.cleaned_data['publish_status'] else None
            schedule_date = form.cleaned_data['schedule_date']
            schedule_time = form.cleaned_data['schedule_time']

            if publish_status and publication.publish_status != publish_status:
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

            return redirect('view_publication', publication.id)
    else:
        schedule_date = publication.publish_schedule.date() if publication.publish_schedule else None
        schedule_time = publication.publish_schedule.time() if publication.publish_schedule else None
        form = MagazineIssueForm(initial={'title':publication.title, 'description':publication.description, 'publish_status':str(publication.publish_status), 'schedule_date':schedule_date, 'schedule_time':schedule_time})
    
    return render(request, 'publication/magazine/publication_edit.html', {'publisher':publisher, 'publication':publication, 'form':form})

# MAGAZINE VIEWS ################################################################################

@login_required
def view_magazines(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not can(request.user, 'view', publisher):
        raise Http404

    magazines = Magazine.objects.filter(publisher=publisher).order_by('-created')

    can_upload_publish = can(request.user, 'upload,publish', publisher)

    for magazine in magazines:
        magazine.published_count = MagazineIssue.objects.filter(magazine=magazine, publication__publish_status=Publication.PUBLISH_STATUS['PUBLISHED']).count()

        try:
            magazine.last_published = MagazineIssue.objects.filter(magazine=magazine, publication__publish_status=Publication.PUBLISH_STATUS['PUBLISHED']).latest('publication__published')
        except MagazineIssue.DoesNotExist:
            magazine.last_published = None
        
        if can_upload_publish:
            magazine.outstanding = {
                'unfinished': UploadingPublication.objects.filter(publisher=publisher, publication_type='magazine', parent_id=magazine.id).count(),
                'scheduled': MagazineIssue.objects.filter(magazine=magazine, publication__publish_status=Publication.PUBLISH_STATUS['SCHEDULED']).count(),
                'unpublished': MagazineIssue.objects.filter(magazine=magazine, publication__publish_status=Publication.PUBLISH_STATUS['UNPUBLISHED']).count(),
            }

    if can_upload_publish:
        outstandings = {
            'unfinished': UploadingPublication.objects.filter(publisher=publisher, publication_type='magazine'),
            'scheduled': Publication.objects.filter(publisher=publisher, publication_type='magazine', publish_status=Publication.PUBLISH_STATUS['SCHEDULED']),
            'unpublished': Publication.objects.filter(publisher=publisher, publication_type='magazine', publish_status=Publication.PUBLISH_STATUS['UNPUBLISHED'])
        }
    else:
        outstandings = None

    return render(request, 'publication/magazine/magazines.html', {'publisher':publisher, 'magazines':magazines, 'outstandings':outstandings})

@login_required
def create_magazine(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not can(request.user, 'manage', publisher):
        raise Http404

    if request.method == 'POST':
        form = MagazineForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            categories = form.cleaned_data['categories']

            magazine = Magazine.objects.create(publisher=publisher, title=title, description=description, created_by=request.user)

            for category in categories:
                magazine.categories.add(category)
            
            return redirect('view_magazine', magazine_id=magazine.id)

    else:
        form = MagazineForm()

    return render(request, 'publication/magazine/magazine_modify.html', {'publisher':publisher, 'form':form})

@login_required
def view_magazine(request, magazine_id):
    magazine = get_object_or_404(Magazine, pk=magazine_id)
    publisher = magazine.publisher

    if not can(request.user, 'view', publisher):
        raise Http404
    
    magazine.issues = MagazineIssue.objects.filter(magazine=magazine, publication__publication_type=MODULE_CODE, publication__publish_status=Publication.PUBLISH_STATUS['PUBLISHED']).order_by('-publication__uploaded')

    if can(request.user, 'upload,publish', publisher):
        outstandings = {
            'unfinished': UploadingPublication.objects.filter(publisher=publisher, publication_type=MODULE_CODE, parent_id=magazine.id),
            'scheduled': Publication.objects.filter(magazineissue__magazine=magazine, publish_status=Publication.PUBLISH_STATUS['SCHEDULED']),
            'unpublished': Publication.objects.filter(magazineissue__magazine=magazine, publish_status=Publication.PUBLISH_STATUS['UNPUBLISHED']),
        }
    else:
        outstandings = None

    return render(request, 'publication/magazine/magazine.html', {'publisher':publisher, 'magazine':magazine, 'outstandings':outstandings})

@login_required
def edit_magazine(request, magazine_id):
    magazine = get_object_or_404(Magazine, pk=magazine_id)
    publisher = magazine.publisher

    if not can(request.user, 'manage', publisher):
        raise Http404

    if request.method == 'POST':
        form = MagazineForm(request.POST)
        if form.is_valid():
            magazine.title = form.cleaned_data['title']
            magazine.description = form.cleaned_data['description']
            categories = form.cleaned_data['categories']
            
            magazine.categories.remove()

            for category in categories:
                magazine.categories.add(category)
            
            magazine.save()

            return redirect('view_magazine', magazine_id=magazine.id)

    else:
        print magazine.categories.all()
        form = MagazineForm(initial={'title':magazine.title, 'description':magazine.description, 'categories':magazine.categories.all()})
    
    return render(request, 'publication/magazine/magazine_modify.html', {'publisher':publisher, 'magazine':magazine, 'form':form})
