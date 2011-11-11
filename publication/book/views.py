import os
import datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import simplejson

from publication import functions as publication_functions
from publication.models import Publisher, Publication

from forms import *
from models import *

# UPLOAD PUBLICATION ################################################################################

def finishing_upload_publication(request, publisher, uploading_publication):
    if request.method == 'POST':
        form = FinishUploadBookForm(request.POST, uploading_publication=uploading_publication)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            author = form.cleaned_data['author']
            publish_status = form.cleaned_data['publish_status']
            schedule_date = form.cleaned_data['schedule_date']
            schedule_time = form.cleaned_data['schedule_time']

            publication = _finishing_upload(publisher, uploading_publication, title, description, publish_status, schedule_date, schedule_time)

            # Create Book object
            
            return redirect('view_publication', publication_id=publication.id)
            
    else:
        form = FinishUploadBookForm(uploading_publication=uploading_publication)
    
    return render(request, 'publication/book/publication_finishing_book_upload.html', {'publisher':publisher, 'uploading_publication':uploading_publication, 'form':form})

# BOOK PUBLICATION ################################################################################

@login_required
def view_book_front(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    books = Publication.objects.filter(publisher=publisher, publication_type='book', publish_status=Publication.PUBLISH_STATUS_PUBLISHED).order_by('uploaded')

    outstandings = {
        'ready': Publication.objects.filter(publisher=publisher, publication_type='book', publish_status=Publication.PUBLISH_STATUS_READY_TO_PUBLISH),
        'scheduled': Publication.objects.filter(publisher=publisher, publication_type='book', publish_status=Publication.PUBLISH_STATUS_SCHEDULE_TO_PUBLISH),
        'unpublished': Publication.objects.filter(publisher=publisher, publication_type='book', publish_status=Publication.PUBLISH_STATUS_UNPUBLISHED),
    }

    return render(request, 'publication/book/books.html', {'publisher':publisher, 'books':books, 'outstandings':outstandings})

@login_required
def view_book(request, book_id):
    return render(request, 'publication/book/book.html', {})

@login_required
def update_book_details(request, book_id):
    return render(request, 'publication/book/book_update_details.html', {})

def upload_book(request, publisher_id):
    return render(request, 'publication/book/book_upload.html', {'form': form})