# -*- encoding: utf-8 -*-

import os
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import simplejson

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

            publish_status = int(form.cleaned_data['publish_status']) if form.cleaned_data['publish_status'] else None
            schedule_date = form.cleaned_data['schedule_date']
            schedule_time = form.cleaned_data['schedule_time']

            publication = publisher_functions.finishing_upload_publication(request, publication, title, description, publish_status, schedule_date, schedule_time)

            book = Book.objects.create(publication=publication, author=author)

            for category in categories:
                book.categories.add(category)
            
            messages.success(request, 'บันทึกข้อมูลเรียบร้อย')

            return redirect('view_books', publisher_id=publisher.id)
            
    else:
        form = FinishUploadBookForm()
    
    return render(request, 'publisher/book/publication_finishing.html', {'publisher':publisher, 'publication':publication, 'form':form})

def cancel_upload_publication(request, publisher, publication):
    # MESSAGE
    return redirect('view_books', publisher_id=publisher.id)

def view_publication(request, publisher, publication):

    return render(request, 'publisher/book/publication.html', {'publisher':publisher, 'publication':publication})

def edit_publication(request, publisher, publication):
    if request.method == 'POST':
        form = EditBookDetailsForm(request.POST)
        if form.is_valid():
            publication.title = form.cleaned_data['title']
            publication.description = form.cleaned_data['description']
            publication.save()

            publication.book.author = form.cleaned_data['author']
            publication.book.save()

            publication.book.categories.clear()

            for category in form.cleaned_data['categories']:
                publication.book.categories.add(category)
            
            # MESSAGE

            return redirect('view_publication', publication.id)
    else:
        form = EditBookDetailsForm(initial={'title':publication.title, 'description':publication.description, 'author':publication.book.author, 'categories':publication.book.categories.all()})

    return render(request, 'publisher/book/publication_edit.html', {'publisher':publisher, 'publication':publication, 'form':form})

def edit_publication_status(request, publisher, publication):
    if request.method == 'POST':
        form = EditBookStatusForm(request.POST)
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
        form = EditBookStatusForm(initial={'publish_status':str(publication.publish_status), 'schedule_date':schedule_date, 'schedule_time':schedule_time})
    
    return render(request, 'publisher/book/publication_edit_status.html', {'publisher':publisher, 'publication':publication, 'form':form})

def delete_publication(request, deleted, publisher, publication):
    if deleted:
        book = Book.objects.get(publication=publication)
        book.delete()

        # MESSAGE

        return redirect('view_books', publisher_id=publisher.id)
        
    else:
        return redirect('view_publication', publication_id=publication.id)

def gather_publisher_statistics(request, publisher):
    return {
        'published_books_count': Publication.objects.filter(publisher=publisher, publication_type='book', publish_status=Publication.PUBLISH_STATUS['PUBLISHED']).count()
    }

# BOOK PUBLICATION ################################################################################

@login_required
def view_books(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not can(request.user, 'view', publisher):
        raise Http404

    books = Publication.objects.filter(publisher=publisher, publication_type='book').order_by('uploaded')

    return render(request, 'publisher/book/books.html', {'publisher':publisher, 'books':books})
