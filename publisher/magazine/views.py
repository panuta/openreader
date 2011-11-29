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
from publisher.models import *

from forms import *
from models import *

# FROM PUBLICATION ################################################################################

def finishing_upload_publication(request, publisher, publication):

    to_create_magazine = ToCreateMagazine.objects.filter(publication=publication).exists()

    if not Magazine.objects.filter(publisher=publisher).exists():
        to_create_magazine = True

    if request.method == 'POST':
        form = FinishUploadMagazineIssueForm(request.POST, publisher=publisher, publication=publication, to_create_magazine=to_create_magazine)
        if form.is_valid():
            magazine = form.cleaned_data['magazine']
            magazine_name = form.cleaned_data['magazine_name']
            categories = form.cleaned_data['categories']

            publisher_functions.finishing_upload_publication(request, publication, form.cleaned_data['title'], form.cleaned_data['description'])

            if to_create_magazine:
                magazine = Magazine.objects.create(publisher=publisher, title=magazine_name, created_by=request.user)

                for category in categories:
                    magazine.categories.add(category)

            magazine_issue = MagazineIssue.objects.get_or_create(publication=publication, magazine=magazine)

            if form.cleaned_data['next']:
                return redirect(form.cleaned_data['next'])

            return redirect('view_magazine', magazine_id=magazine.id)

    else:
        form = FinishUploadMagazineIssueForm(initial={'next':request.GET.get('from', '')}, publisher=publisher, publication=publication, to_create_magazine=to_create_magazine)
    
    try:
        magazine = MagazineIssue.objects.get(publication=publication).magazine
    except MagazineIssue.DoesNotExist:
        magazine = None
    
    return render(request, 'publisher/magazine/publication_finishing.html', {'publisher':publisher, 'publication':publication, 'form':form, 'to_create_magazine':to_create_magazine, 'magazine':magazine})

def cancel_upload_publication(request, publisher, publication):
    magazine_issue = MagazineIssue.objects.get(publication=publication)
    Magazine.objects.filter(cancel_with_issue=publication.magazineissue).delete()
    publication.magazineissue.delete()

    # MESSAGE

    return redirect('view_magazines', publisher_id=publisher.id)

def view_publication(request, publisher, publication):

    return render(request, 'publisher/magazine/publication.html', {'publisher':publisher, 'publication':publication})

def edit_publication(request, publisher, publication):
    if request.method == 'POST':
        form = EditMagazineIssueDetailsForm(request.POST)
        if form.is_valid():
            publication.title = form.cleaned_data['title']
            publication.description = form.cleaned_data['description']
            publication.save()

            # MESSAGE

            return redirect('view_publication', publication.id)
    else:
        form = EditMagazineIssueDetailsForm(initial={'title':publication.title, 'description':publication.description})
    
    return render(request, 'publisher/magazine/publication_edit.html', {'publisher':publisher, 'publication':publication, 'form':form})

def edit_publication_status(request, publisher, publication):
    if request.method == 'POST':
        form = EditMagazineIssueStatusForm(request.POST)
        if form.is_valid():
            publish_status = int(form.cleaned_data['publish_status']) if form.cleaned_data['publish_status'] else None
            schedule_date = form.cleaned_data['schedule_date']
            schedule_time = form.cleaned_data['schedule_time']

            publication.publish_status = publish_status

            if publish_status == Publication.STATUS['UNPUBLISHED']:
                publication.publish_schedule = None
                publication.published = None
                publication.published_by = None

            elif publish_status == Publication.STATUS['SCHEDULED']:
                publication.publish_schedule = datetime.datetime(schedule_date.year, schedule_date.month, schedule_date.day, schedule_time.hour, schedule_time.minute)
                publication.published = None
                publication.published_by = request.user

            elif publish_status == Publication.STATUS['PUBLISHED']:
                publication.publish_schedule = None
                publication.published = datetime.datetime.today()
                publication.published_by = request.user
            
            publication.save()

            # MESSAGE

            return redirect('view_publication', publication.id)

    else:
        schedule_date = publication.publish_schedule.date() if publication.publish_schedule else None
        schedule_time = publication.publish_schedule.time() if publication.publish_schedule else None
        form = EditMagazineIssueStatusForm(initial={'publish_status':str(publication.publish_status), 'schedule_date':schedule_date, 'schedule_time':schedule_time})
    
    return render(request, 'publisher/magazine/publication_edit_status.html', {'publisher':publisher, 'publication':publication, 'form':form})

def delete_publication(request, deleted, publisher, publication):
    if deleted:
        magazine_issue = MagazineIssue.objects.get(publication=publication)
        magazine_issue.delete()

        # MESSAGE

        return redirect('view_magazine', magazine_id=magazine_issue.magazine.id)
    
    else:
        return redirect('view_publication', publication_id=publication.id)

def gather_publisher_statistics(request, publisher):
    return {
        'magazine_count': Magazine.objects.filter(publisher=publisher).count(),
        'published_issue_count': Publication.objects.filter(publisher=publisher, publication_type='magazine', status=Publication.STATUS['PUBLISHED']).count()
    }

# MAGAZINE VIEWS ################################################################################

@login_required
def view_magazines(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not has_module(publisher, 'magazine') or not can(request.user, 'view', publisher):
        raise Http404

    magazines = Magazine.objects.filter(publisher=publisher).order_by('-created')

    if can(request.user, 'edit', publisher):
        uploading_publications = Publication.objects.filter(status=Publication.STATUS['UPLOADING'], publication_type='magazine')
        orphan_publications = []
        for uploading_publication in uploading_publications:
            if not MagazineIssue.objects.filter(publication=uploading_publication).exists():
                orphan_publications.append(uploading_publication)
    else:
        orphan_publications = None
    
    recent_issues = MagazineIssue.objects.filter(publication__publisher=publisher).exclude(publication__status=Publication.STATUS['UPLOADING']).order_by('-publication__uploaded')[0:10]

    return render(request, 'publisher/magazine/magazines.html', {'publisher':publisher, 'magazines':magazines, 'recent_issues':recent_issues, 'orphan_publications':orphan_publications})

@login_required
def create_magazine(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not has_module(publisher, 'magazine') or not can(request.user, 'edit', publisher):
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
            
            # MESSAGE
            
            return redirect('view_magazine', magazine_id=magazine.id)

    else:
        form = MagazineForm()

    return render(request, 'publisher/magazine/magazine_modify.html', {'publisher':publisher, 'form':form})

@login_required
def view_magazine(request, magazine_id):
    magazine = get_object_or_404(Magazine, pk=magazine_id)
    publisher = magazine.publisher

    if not has_module(publisher, 'magazine') or not can(request.user, 'view', publisher):
        raise Http404
    
    magazine.issues = MagazineIssue.objects.filter(magazine=magazine, publication__publication_type='magazine').order_by('-publication__uploaded')

    return render(request, 'publisher/magazine/magazine.html', {'publisher':publisher, 'magazine':magazine})

@login_required
def edit_magazine(request, magazine_id):
    magazine = get_object_or_404(Magazine, pk=magazine_id)
    publisher = magazine.publisher

    if not has_module(publisher, 'magazine') or not can(request.user, 'edit', publisher):
        raise Http404

    if request.method == 'POST':
        form = MagazineForm(request.POST)
        if form.is_valid():
            magazine.title = form.cleaned_data['title']
            magazine.description = form.cleaned_data['description']
            categories = form.cleaned_data['categories']
            
            magazine.categories.clear()

            for category in categories:
                magazine.categories.add(category)
            
            magazine.save()

            # MESSAGE

            return redirect('view_magazine', magazine_id=magazine.id)

    else:
        form = MagazineForm(initial={'title':magazine.title, 'description':magazine.description, 'categories':magazine.categories.all()})
    
    return render(request, 'publisher/magazine/magazine_modify.html', {'publisher':publisher, 'magazine':magazine, 'form':form})

@login_required
def delete_magazine(request, magazine_id):
    magazine = get_object_or_404(Magazine, pk=magazine_id)
    publisher = magazine.publisher

    if not has_module(publisher, 'magazine') or not can(request.user, 'edit', publisher):
        raise Http404
    
    if request.method == 'POST':
        if 'submit-delete' in request.POST:
            from publisher.functions import delete_uploading_publication

            for magazine_issue in MagazineIssue.objects.filter(magazine=magazine):
                delete_uploading_publication(magazine_issue.publication)
                magazine_issue.delete()
            
            magazine.delete()

            # MESSAGE
        
            return redirect('view_magazines', publisher_id=publisher.id)

        else:
            return redirect('view_magazine', magazine_id=magazine.id)
    
    magazine.issue_count = MagazineIssue.objects.filter(magazine=magazine).count()

    return render(request, 'publisher/magazine/magazine_delete.html', {'publisher':publisher, 'magazine':magazine})
