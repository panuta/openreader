# -*- encoding: utf-8 -*-

import os
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import simplejson

from common.modules import has_module
from common.permissions import can

from publisher import functions as publisher_functions
from publisher.forms import PublisherShelfForm
from publisher.models import Publisher, Publication, PublisherShelf, PublicationShelf

from forms import *
from models import *

# PUBLICATION ################################################################################

def finishing_upload_publication(request, publisher, publication):
    if request.method == 'POST':
        form = FinishUploadFileForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            
            publication = publisher_functions.finishing_upload_publication(request, publication, title, description)

            if has_module(publisher, 'shelf'):
                publication.shelves.clear()
                for shelf in form.cleaned_data['shelf']:
                    PublicationShelf.objects.create(publication=publication, shelf=shelf, created_by=request.user)

            if form.cleaned_data['next']:
                return redirect(form.cleaned_data['next'])

            return redirect('view_files', publisher_id=publisher.id)
            
    else:
        shelves = PublicationShelf.objects.filter(publication=publication).values_list('shelf', flat=True)
        form = FinishUploadFileForm(initial={'next':request.GET.get('from', ''), 'shelf':shelves})
    
    return render(request, 'publisher/file/publication_finishing.html', {'publisher':publisher, 'publication':publication, 'form':form})

def cancel_upload_publication(request, publisher, publication):
    return redirect('view_files', publisher_id=publisher.id)

def edit_publication(request, publisher, publication):
    if request.method == 'POST':
        form = EditFilePublicationForm(request.POST)
        if form.is_valid():
            publication.title = form.cleaned_data['title']
            publication.description = form.cleaned_data['description']

            if has_module(publisher, 'shelf'):
                new_shelves = set(form.cleaned_data['shelf']) # PublisherShelf model

                old_shelves = set()
                for shelf in publication.shelves.all():
                    old_shelves.add(shelf.shelf)

                creating_shelves = new_shelves.difference(old_shelves)
                removing_shelves = old_shelves.difference(new_shelves)

                for shelf in creating_shelves:
                    PublicationShelf.objects.create(publication=publication, shelf=shelf, created_by=request.user)

                PublicationShelf.objects.filter(publication=publication, shelf__in=removing_shelves).delete()
            
            publication.save()
            
            messages.success(request, u'แก้ไขรายละเอียดเรียบร้อย')
            if request.POST.get('from_page'):
                return redirect(request.POST.get('from_page'))

            return redirect('view_publication', publication.id)
    else:
        form = EditFilePublicationForm(initial={'title':publication.title, 'description':publication.description, 'from_page':request.GET.get('from')})

    return render(request, 'publisher/file/publication_edit.html', {'publisher':publisher, 'publication':publication, 'form':form})

def delete_publication(request, deleted, publisher, publication):
    return redirect('view_files', publisher_id=publisher.id)

def gather_publisher_statistics(request, publisher):
    return {
        'published_files_count': Publication.objects.filter(publisher=publisher, publication_type='file', status=Publication.STATUS['PUBLISHED']).count()
    }

# FILE PUBLICATION ################################################################################

@login_required
def view_files(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not has_module(publisher, 'file'):
        raise Http404
    
    if not can(request.user, 'view', publisher):
        raise Http404
    
    if can(request.user, 'edit', publisher):
        files = Publication.objects.filter(publisher=publisher, publication_type='file').order_by('-uploaded')
    else:
        files = Publication.objects.filter(publisher=publisher, publication_type='file', status=Publication.STATUS['PUBLISHED']).order_by('-uploaded')

    return render(request, 'publisher/file/files.html', {'publisher':publisher, 'files':files})

@login_required
def view_files_no_shelf(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not has_module(publisher, 'file'):
        raise Http404

    if not can(request.user, 'view', publisher):
        raise Http404
    
    if can(request.user, 'edit', publisher):
        files = Publication.objects.filter(publisher=publisher, publication_type='file', shelves=None).order_by('-uploaded')
    else:
        files = Publication.objects.filter(publisher=publisher, publication_type='file', shelves=None, status=Publication.STATUS['PUBLISHED']).order_by('-uploaded')

    return render(request, 'publisher/file/files.html', {'publisher':publisher, 'files':files, 'shelf':'noshelf'})

@login_required
def view_files_by_shelf(request, shelf_id):
    shelf = get_object_or_404(PublisherShelf, pk=shelf_id)
    publisher = shelf.publisher

    if shelf.publisher.id != publisher.id or not has_module(publisher, 'file') or not has_module(publisher, 'shelf'):
        raise Http404
    
    if not can(request.user, 'view', publisher):
        raise Http404
    
    if can(request.user, 'edit', publisher):
        files = Publication.objects.filter(publisher=publisher, publication_type='file', shelves__in=[shelf]).order_by('-uploaded')
    else:
        files = Publication.objects.filter(publisher=publisher, publication_type='file', shelves__in=[shelf], status=Publication.STATUS['PUBLISHED']).order_by('-uploaded')
    
    return render(request, 'publisher/file/files.html', {'publisher':publisher, 'files':files, 'shelf':shelf})

@login_required
def create_file_shelf(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not has_module(publisher, 'shelf') or not can(request.user, 'manage', publisher):
        raise Http404
    
    if request.method == 'POST':
        form = PublisherShelfForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']

            shelf = PublisherShelf.objects.create(publisher=publisher, name=name, description=description, created_by=request.user)

            messages.success(request, u'เพิ่มชั้นหนังสือเรียบร้อย')

            return redirect('view_files_by_shelf', shelf_id=shelf.id)
    else:
        form = PublisherShelfForm()
    
    return render(request, 'publisher/file/file_shelf_modify.html', {'publisher':publisher, 'form':form})

@login_required
def edit_file_shelf(request, shelf_id):
    shelf = get_object_or_404(PublisherShelf, pk=shelf_id)
    publisher = shelf.publisher

    if not has_module(publisher, 'shelf') or not can(request.user, 'manage', publisher):
        raise Http404
    
    if request.method == 'POST':
        form = PublisherShelfForm(request.POST)
        if form.is_valid():
            shelf.name = form.cleaned_data['name']
            shelf.description = form.cleaned_data['description']
            shelf.save()

            messages.success(request, u'แก้ไขชั้นหนังสือเรียบร้อย')

            return redirect('view_files_by_shelf', shelf_id=shelf.id)
    else:
        form = PublisherShelfForm(initial={'name':shelf.name, 'description':shelf.description})
    
    return render(request, 'publisher/file/file_shelf_modify.html', {'publisher':publisher, 'form':form, 'shelf':shelf})