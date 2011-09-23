import os

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render

from publication import functions as publication_functions

from forms import *
from models import *

from membership.models import UserPublisher

# Publisher Dashboard ######################################################################

@login_required
def view_dashboard(request):
    try:
        default_publisher = UserPublisher.objects.get(user=request.user, is_default=True)
        return redirect('view_publisher_dashboard', publisher_id=default_publisher.id)
    except UserPublisher.DoesNotExist:
        if UserPublisher.objects.filter(user=request.user).count() == 0:
            return redirect('view_user_welcome')
        else:
            # If a user does not set any default publisher, redirect to publisher selection
            return redirect('select_publisher')

@login_required
def view_publisher_dashboard(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    return render(request, 'publication/dashboard.html', {'publisher':publisher})

def select_publisher(request):
    user_publishers = UserPublisher.objects.filter(user=request.user)
    return render(request, 'publication/publisher_select.html', {'user_publishers':user_publishers})

@login_required
def create_publisher(request):
    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():
            publisher = form.save(commit=False)
            publisher.created_by = request.user
            publisher.modified_by = request.user
            publisher.save()

            user_publisher = UserPublisher.objects.create(user=request.user, publisher=publisher)

            if UserPublisher.objects.filter(user=request.user).count() == 1:
                user_publisher.is_default = True
                user_publisher.save()

            return redirect('view_publisher_dashboard', publisher_id=publisher.id)
    else:
        form = PublisherForm()
    
    return render(request, 'publication/publisher_create.html', {'form': form})

@login_required
def update_publisher(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():
            publisher = form.save(commit=False)
            publisher.modified_by = request.user
            publisher.save()

            return redirect('view_publisher_dashboard', publisher_id=publisher.id)
    else:
        form = PublisherForm(initial=publisher)
    
    return render(request, 'publication/publisher_update.html', {'form': form})

def deactivate_publisher(request, publisher_id):
    pass

# Publisher Periodicals ######################################################################

@login_required
def view_publisher_periodicals(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    return render(request, 'publication/periodicals.html', {'publisher':publisher})

@login_required
def view_periodical(request, periodical_id):
    return render(request, 'publication/periodical.html', {})

@login_required
def update_periodical(request, periodical_id):
    return render(request, 'publication/periodical_update.html', {})

@login_required
def view_periodical_issue(request, periodical_issue_id):
    return render(request, 'publication/periodical_issue.html', {})

@login_required
def update_periodical_issue_details(request, periodical_issue_id):
    return render(request, 'publication/periodical_issue_update_details.html', {})

@login_required
def upload_periodical_issue(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if request.method == 'POST':
        form = UploadPeriodicalIssueForm(request.POST)
        if form.is_valid():
            publication_uid = form.cleaned_data['publication_uid']
            periodical = form.cleaned_data['periodical']
            issue_name = form.cleaned_data['issue_name']
            description = form.cleaned_data['description']

            uploading_publication = UploadingPublication.objects.get(uid=publication_uid)

            publication = Publication.objects.create(
                uid=publication_uid,
                file_path='%d/%s.%s' % (publisher.id, publication_uid, uploading_publication.file_ext),
                file_ext=uploading_publication.file_ext,
                publish_status=Publication.PUBLISH_STATUS_UNPUBLISHED,
                uploaded_by=request.user,
                modified_by=request.user,
            )

            issue = PeriodicalIssue.objects.create(
                publication=publication,
                periodical=periodical,
                issue_name=issue_name,
                description=description,

                created_by=request.user,
                modified_by=request.user,
            )

            return redirect('view_periodical_issue', periodical_issue_id=issue.id)

    else:
        form = UploadPeriodicalIssueForm()
    
    return render(request, 'publication/periodical_upload.html', {'publisher':publisher, 'form':form})

@login_required
def uploading_periodical_issue(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if request.method == 'POST':
        try:
            periodical = request.POST.get('periodical', None)
            uploading_file = request.FILES['publication']

            if uploading_file:
                uid = publication_functions.upload_publication(request.user, uploading_file, publisher, UploadingPublication.UPLOADING_PERIODICAL_ISSUE, periodical)
                return HttpResponse(uid)
            else:
                return HttpResponse('')
        except:
            import sys
            print sys.exc_info()
            return HttpResponse('')
    
    else:
        raise Http404

@login_required
def get_upload_progress(request):
    """
    Return JSON object with information about the progress of an upload.
    """
    progress_id = ''
    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']
    if progress_id:
        from django.utils import simplejson
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        print "get_progress -> key -> %s" % cache_key
        data = cache.get(cache_key)
        print data
        return HttpResponse(simplejson.dumps(data))
    else:
        return HttpResponseServerError('Server Error: You must provide X-Progress-ID header or query param.')


# Publisher Books ######################################################################

@login_required
def view_publisher_books(request, publisher_id):
    return render(request, 'publication/books.html', {})

@login_required
def view_book(request, book_id):
    return render(request, 'publication/book.html', {})

@login_required
def update_book_details(request, book_id):
    return render(request, 'publication/book_update_details.html', {})

def upload_book(request, publisher_id):
    return render(request, 'publication/book_upload.html', {'form': form})

# Publisher Management ######################################################################

@login_required
def view_publisher_profile(request, publisher_id):
    return render(request, 'publication/publisher_profile.html', {})

@login_required
def view_publisher_team(request, publisher_id):
    return render(request, 'publication/publisher_team.html', {})

@login_required
def view_publisher_team_invite(request, publisher_id):
    return render(request, 'publication/publisher_team_invite.html', {})

