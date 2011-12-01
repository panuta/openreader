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
        form = FinishUploadBookForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            author = form.cleaned_data['author']
            categories = form.cleaned_data['categories']

            publication = publisher_functions.finishing_upload_publication(request, publication, title, description)

            book = Book.objects.create(publication=publication, author=author)

            for category in categories:
                book.categories.add(category)
            
            if form.cleaned_data['next']:
                return redirect(form.cleaned_data['next'])

            return redirect('view_books', publisher_id=publisher.id)
            
    else:
        form = FinishUploadBookForm(initial={'next':request.GET.get('from', '')})
    
    return render(request, 'publisher/book/publication_finishing.html', {'publisher':publisher, 'publication':publication, 'form':form})

def cancel_upload_publication(request, publisher, publication):
    return redirect('view_books', publisher_id=publisher.id)

def edit_publication(request, publisher, publication):
    if request.method == 'POST':
        form = EditBookPublicationForm(request.POST)
        if form.is_valid():
            publication.title = form.cleaned_data['title']
            publication.description = form.cleaned_data['description']
            publication.save()

            publication.book.author = form.cleaned_data['author']
            publication.book.save()

            publication.book.categories.clear()

            for category in form.cleaned_data['categories']:
                publication.book.categories.add(category)
            
            messages.success(request, u'แก้ไขรายละเอียดเรียบร้อย')
            if request.POST.get('from_page'):
                return redirect(request.POST.get('from_page'))

            return redirect('view_publication', publication.id)
    else:
        form = EditBookPublicationForm(initial={'title':publication.title, 'description':publication.description, 'author':publication.book.author, 'categories':publication.book.categories.all(), 'from_page':request.GET.get('from')})

    return render(request, 'publisher/book/publication_edit.html', {'publisher':publisher, 'publication':publication, 'form':form})

def delete_publication(request, deleted, publisher, publication):
    book = Book.objects.get(publication=publication)
    book.delete()
    return redirect('view_books', publisher_id=publisher.id)

def gather_publisher_statistics(request, publisher):
    return {
        'published_books_count': Publication.objects.filter(publisher=publisher, publication_type='book', status=Publication.STATUS['PUBLISHED']).count()
    }

# BOOK PUBLICATION ################################################################################

@login_required
def view_books(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not has_module(publisher, 'book') or not can(request.user, 'view', publisher):
        raise Http404
    
    if can(request.user, 'edit', publisher):
        books = Publication.objects.filter(publisher=publisher, publication_type='book').order_by('-uploaded')
    else:
        books = Publication.objects.filter(publisher=publisher, publication_type='book', status=Publication.STATUS['PUBLISHED']).order_by('-uploaded')
    
    return render(request, 'publisher/book/books.html', {'publisher':publisher, 'books':books})
