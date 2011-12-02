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
    to_create_magazine = not Magazine.objects.filter(publisher=publisher).exists()
    
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
    try:
        magazine_issue = MagazineIssue.objects.get(publication=publication).delete()
    except MagazineIssue.DoesNotExist:
        pass
    
    return redirect('view_magazines', publisher_id=publisher.id)

def edit_publication(request, publisher, publication):
    if request.method == 'POST':
        form = EditMagazinePublicationForm(request.POST)
        if form.is_valid():
            publication.title = form.cleaned_data['title']
            publication.description = form.cleaned_data['description']
            publication.save()

            messages.success(request, u'แก้ไขรายละเอียดเรียบร้อย')
            if request.POST.get('from_page'):
                return redirect(request.POST.get('from_page'))

            return redirect('view_publication', publication.id)
    else:
        form = EditMagazinePublicationForm(initial={'title':publication.title, 'description':publication.description, 'from_page':request.GET.get('from')})
    
    return render(request, 'publisher/magazine/publication_edit.html', {'publisher':publisher, 'publication':publication, 'form':form})

def delete_publication(request, deleted, publisher, publication):
    magazine_issue = MagazineIssue.objects.get(publication=publication)
    magazine_issue.delete()
    return redirect('view_magazine', magazine_id=magazine_issue.magazine.id)

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
        uploading_publications = Publication.objects.filter(status=Publication.STATUS['UPLOADED'], publication_type='magazine')
        orphan_publications = []
        for uploading_publication in uploading_publications:
            if not MagazineIssue.objects.filter(publication=uploading_publication).exists():
                orphan_publications.append(uploading_publication)
    else:
        orphan_publications = None
    
    if can(request.user, 'edit', publisher):
        recent_issues = MagazineIssue.objects.filter(publication__publisher=publisher).order_by('-publication__uploaded')
    else:
        recent_issues = MagazineIssue.objects.filter(publication__publisher=publisher, publication__status=Publication.STATUS['PUBLISHED']).order_by('-publication__uploaded')

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
            
            messages.success(request, u'สร้างนิตยสารเรียบร้อย')
            
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
    
    if can(request.user, 'edit', publisher):
        magazine_issues = MagazineIssue.objects.filter(magazine=magazine, publication__publication_type='magazine').order_by('-publication__uploaded')
    else:
        magazine_issues = MagazineIssue.objects.filter(magazine=magazine, publication__publication_type='magazine', publication__status=Publication.STATUS['PUBLISHED']).order_by('-publication__uploaded')

    return render(request, 'publisher/magazine/magazine.html', {'publisher':publisher, 'magazine':magazine, 'magazine_issues':magazine_issues})

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
            
            messages.success(request, u'แก้ไขนิตยสารเรียบร้อย')
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
            
            for magazine_issue in MagazineIssue.objects.filter(magazine=magazine):
                publisher_functions.delete_publication(magazine_issue.publication)
                magazine_issue.delete()
            
            magazine.delete()

            messages.success(request, u'ลบนิตยสารเรียบร้อย')
            return redirect('view_magazines', publisher_id=publisher.id)

        else:
            return redirect('view_magazine', magazine_id=magazine.id)
    
    magazine.issue_count = MagazineIssue.objects.filter(magazine=magazine).count()

    return render(request, 'publisher/magazine/magazine_delete.html', {'publisher':publisher, 'magazine':magazine})
