import os
import datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import simplejson

from publication import functions as publication_functions
from publication.models import *

from publication.magazine import MODULE_CODE
#from exceptions import *
from forms import *
from models import *

# PUBLICATION ################################################################################

def finishing_upload_publication(request, publisher, uploading_publication):
    if request.method == 'POST':
        form = FinishUploadMagazineIssueForm(request.POST, publisher=publisher, uploading_publication=uploading_publication)
        if form.is_valid():
            magazine = form.cleaned_data['magazine']
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            publish_status = form.cleaned_data['publish_status']
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

    return render(request, 'publication/magazine/magazine_issue.html', {'publisher':publisher, 'publication':publication})

# MAGAZINE VIEWS ################################################################################

@login_required
def view_publisher_magazines(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    magazines = Magazine.objects.filter(publisher=publisher).order_by('-created')

    for magazine in magazines:
        magazine.published_count = MagazineIssue.objects.filter(magazine=magazine, publication__publish_status=Publication.PUBLISH_STATUS_PUBLISHED).count()

        try:
            magazine.last_published = MagazineIssue.objects.filter(magazine=magazine, publication__publish_status=Publication.PUBLISH_STATUS_PUBLISHED).latest('publication__published')
        except MagazineIssue.DoesNotExist:
            magazine.last_published = None
        
        magazine.outstanding = {
            'ready': MagazineIssue.objects.filter(magazine=magazine, publication__publish_status=Publication.PUBLISH_STATUS_READY_TO_PUBLISH).count(),
            'scheduled': MagazineIssue.objects.filter(magazine=magazine, publication__publish_status=Publication.PUBLISH_STATUS_SCHEDULE_TO_PUBLISH).count(),
            'unpublished': MagazineIssue.objects.filter(magazine=magazine, publication__publish_status=Publication.PUBLISH_STATUS_UNPUBLISHED).count(),
        }

    outstandings = {
        'ready': Publication.objects.filter(publisher=publisher, publish_status=Publication.PUBLISH_STATUS_READY_TO_PUBLISH),
        'scheduled': Publication.objects.filter(publisher=publisher, publish_status=Publication.PUBLISH_STATUS_SCHEDULE_TO_PUBLISH),
        'unpublished': Publication.objects.filter(publisher=publisher, publish_status=Publication.PUBLISH_STATUS_UNPUBLISHED)
    }

    return render(request, 'publication/magazine/magazines.html', {'publisher':publisher, 'magazines':magazines, 'outstandings':outstandings})

@login_required
def create_publisher_magazine(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if request.method == 'POST':
        form = PublisherMagazineForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']

            Magazine.objects.create(publisher=publisher, title=title, description=description, created_by=request.user)
            
            return redirect('view_publisher_magazines', publisher_id=publisher.id)

    else:
        form = PublisherMagazineForm()

    return render(request, 'publication/magazine/magazine_modify.html', {'publisher':publisher, 'form':form})

@login_required
def view_magazine(request, magazine_id):
    magazine = get_object_or_404(Magazine, pk=magazine_id)
    publisher = magazine.publisher

    magazine.issues = MagazineIssue.objects.filter(magazine=magazine, publication__publication_type=MODULE_CODE, publication__publish_status=Publication.PUBLISH_STATUS_PUBLISHED).order_by('-publication__uploaded')

    outstandings = {
        'ready': Publication.objects.filter(magazineissue__magazine=magazine, publish_status=Publication.PUBLISH_STATUS_READY_TO_PUBLISH),
        'scheduled': Publication.objects.filter(magazineissue__magazine=magazine, publish_status=Publication.PUBLISH_STATUS_SCHEDULE_TO_PUBLISH),
        'unpublished': Publication.objects.filter(magazineissue__magazine=magazine, publish_status=Publication.PUBLISH_STATUS_UNPUBLISHED),
    }

    return render(request, 'publication/magazine/magazine.html', {'publisher':publisher, 'magazine':magazine, 'outstandings':outstandings})

@login_required
def edit_magazine(request, magazine_id):
    magazine = get_object_or_404(Magazine, pk=magazine_id)
    publisher = magazine.publisher

    if request.method == 'POST':
        form = PublisherMagazineForm(request.POST)
        if form.is_valid():
            magazine.title = form.cleaned_data['title']
            magazine.description = form.cleaned_data['description']

            magazine.save()

            return redirect('view_magazine', magazine_id=magazine.id)

    else:
        form = PublisherMagazineForm(initial={'title':magazine.title, 'description':magazine.description})
    
    return render(request, 'publication/magazine/magazine_modify.html', {'publisher':publisher, 'magazine':magazine, 'form':form})

@login_required
def view_magazine_issue(request, magazine_issue_id):
    return render(request, 'publication/magazine/magazine_issue.html', {})

@login_required
def update_magazine_issue_details(request, magazine_issue_id):
    return render(request, 'publication/magazine/magazine_issue_update_details.html', {})
