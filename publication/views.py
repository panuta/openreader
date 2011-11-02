import os
import datetime

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import simplejson

from private_files.views import get_file as private_files_get_file

from common.shortcuts import response_json, response_json_error

from publication import SUPPORT_PUBLICATION_TYPE
from publication import functions as publication_functions

from exceptions import *
from forms import *
from models import *

from accounts.models import UserPublisher

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

@login_required
def select_publisher(request):
    user_publishers = UserPublisher.objects.filter(user=request.user)
    return render(request, 'publication/publisher_select.html', {'user_publishers':user_publishers})

@login_required
def create_publisher(request):
    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():
            publisher_name = form.cleaned_data['name']

            publisher = Publisher.objects.create(name=publisher_name, created_by=request.user, modified_by=request.user)
            PublisherShelf.objects.create(publisher=publisher, created_by=request.user)

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
            publisher_name = form.cleaned_data['name']

            publisher.name = publisher_name
            publisher.modified_by = request.user
            publisher.save()

            return redirect('view_publisher_dashboard', publisher_id=publisher.id)
    else:
        form = PublisherForm(initial=publisher)
    
    return render(request, 'publication/publisher_update.html', {'form': form})

@login_required
def deactivate_publisher(request, publisher_id):
    pass

# Publication ######################################################################

@login_required
def upload_publication(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    pre_upload_type = request.GET.get('type', '')
    pre_upload_periodical = request.GET.get('periodical', '')

    if pre_upload_type == 'periodical' and pre_upload_periodical:
        try:
            pre_upload_periodical = Periodical.objects.get(id=pre_upload_periodical)
        except Periodical.DoesNotExist:
            raise Http404

    


    if request.method == 'POST':
        form = UploadPublicationForm(request.POST, request.FILES)
        if form.is_valid():
            publication_type = form.cleaned_data['type']
            uploading_file = form.cleaned_data['publication']

            periodical_id = None

            return HttpResponse(simplejson.dumps({'error':'something', 'any':'thing'}))

            if publication_type == 'periodical-issue':
                publication_type = 'periodical'
                periodical_id = request.POST.get('periodical')
                if not periodical_id or not Periodical.objects.filter(id=periodical_id).exists():
                    return 'error'

            elif not publication_type:
                publication_type = request.POST.get('publication_type')
                if publication_type and publication_type in ('periodical', 'book'):
                    publication_type = publication_type
                else:
                    return 'error'
            
            try:
                uploading_publication = publication_functions.upload_publication(request.user, uploading_file, publisher, publication_type, periodical_id)
            except:
                form.errors['publication'] = 'ERROR'
                # TODO add message
            
            if request.is_ajax():
                return HttpResponse(reverse('finishing_upload_publication', args=[uploading_publication.id]))
            else:
                return redirect('finishing_upload_publication', uploading_publication.id)

        else:
            if request.is_ajax():
                # TODO
                return 'error-code'

    else:
        form = UploadPublicationForm()
    
    return render(request, 'publication/publication_upload.html', {'publisher':publisher, 'form':form, 'pre_upload_type':pre_upload_type, 'pre_upload_periodical':pre_upload_periodical})

@login_required
def ajax_upload_publication(request, publisher_id):

    if request.method == 'POST':
        try:
            publisher = Publisher.objects.get(id=publisher_id)
        except Publisher.DoesNotExist:
            return response_json_error('publisher-notexist')

        form = UploadPublicationForm(request.POST, request.FILES)
        if form.is_valid():
            upload_type = form.cleaned_data['type']
            uploading_file = form.cleaned_data['publication']
            periodical_id = None

            if upload_type == 'periodical':
                periodical_id = request.POST.get('periodical')
                if not periodical_id or not Periodical.objects.filter(id=periodical_id).exists():
                    return response_json_error('invalid-periodical')

            elif upload_type == 'periodical-issue':
                upload_type = 'periodical'
                periodical_id = request.POST.get('periodical_id')
                if not periodical_id or not Periodical.objects.filter(id=periodical_id).exists():
                    return response_json_error('invalid-periodical')
            
            elif not upload_type:
                publication_type = request.POST.get('publication_type')
                if publication_type and publication_type in SUPPORT_PUBLICATION_TYPE:
                    upload_type = publication_type
                else:
                    return response_json_error('invalid-publication_type')
            
            try:
                uploading_publication = publication_functions.upload_publication(request.user, uploading_file, publisher, upload_type, periodical_id)
            except FileUploadTypeUnknown:
                return response_json_error('upload-unknown')
            except:
                return response_json_error('upload')
            
            return response_json({'next_url':reverse('finishing_upload_publication', args=[uploading_publication.id])})

        else:
            return response_json_error('missing-fields')
        
    else:
        raise Http404

"""
@login_required
def upload_publication(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    pre_upload_type = request.GET.get('type', '')
    pre_upload_periodical = request.GET.get('periodical', '')

    if pre_upload_type == 'periodical' and pre_upload_periodical:
        try:
            periodical = Periodical.objects.get(id=pre_upload_periodical)
        except Periodical.DoesNotExist:
            periodical = None
    else:
        periodical = None

    if request.method == 'POST':
        form = UploadPublicationForm(request.POST)
        if form.is_valid():
            uploading_file = form.cleaned_data['publication']

            try:
                uploading_publication = publication_functions.upload_publication(request.user, uploading_file, publisher)
            except:
                # TODO add message
                pass
            else:
                if request.is_ajax():
                    return HttpResponse(uploading_publication.id)
                else:
                    return response('finish_upload_publication', publication.id)
    
    else:
        form = UploadPublicationForm()
    
    return render(request, 'publication/publication_upload.html', {'publisher':publisher, 'form':form, 'pre_upload_type':pre_upload_type, 'periodical':periodical})
"""

@login_required
def finishing_upload_publication(request, publication_id):
    uploading_publication = get_object_or_404(UploadingPublication, pk=publication_id)
    publisher = uploading_publication.publisher

    if uploading_publication.publication_type == 'periodical':
        return finishing_upload_periodical_issue(request, publisher, uploading_publication)
        
    elif uploading_publication.publication_type == 'book':
        return finishing_upload_book(request, publisher, uploading_publication)

    else:
        raise Http404

def _finishing_upload(publisher, uploading_publication, title, description, publish_status, schedule_date, schedule_time):
    from common.utilities import convert_publish_status
    publish_status = convert_publish_status(publish_status)

    if publish_status == Publication.PUBLISH_STATUS_SCHEDULE_TO_PUBLISH:
        publish_schedule = datetime.datetime(schedule_date.year, schedule_date.month, schedule_date.day, schedule_time.hour, schedule_time.minute)
    else:
        publish_schedule = None

    if publish_status == Publication.PUBLISH_STATUS_PUBLISHED:
        published = datetime.datetime.today()
        published_by = request.user
    else:
        published = None
        published_by = None
    
    publication = Publication.objects.create(
        publisher = publisher,
        uid = uploading_publication.uid,
        title = title,
        description = description,
        publication_type = uploading_publication.publication_type,
        uploaded_file = uploading_publication.uploaded_file,
        original_file_name = uploading_publication.original_file_name,
        file_ext = uploading_publication.file_ext,

        publish_status = publish_status,
        published = published,
        published_by = published_by,

        uploaded = uploading_publication.uploaded,
        uploaded_by = uploading_publication.uploaded_by,
    )

    uploading_publication.delete()
    
    return publication

def finishing_upload_periodical_issue(request, publisher, uploading_publication):
    if request.method == 'POST':
        form = FinishUploadPeriodicalIssueForm(request.POST, publisher=publisher, uploading_publication=uploading_publication)
        if form.is_valid():
            periodical = form.cleaned_data['periodical']
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            publish_status = form.cleaned_data['publish_status']
            schedule_date = form.cleaned_data['schedule_date']
            schedule_time = form.cleaned_data['schedule_time']

            publication = _finishing_upload(publisher, uploading_publication, title, description, publish_status, schedule_date, schedule_time)

            if uploading_publication.parent_id:
                periodical = Periodical.objects.get(id=uploading_publication.parent_id)
            PeriodicalIssue.objects.create(publication=publication, periodical=periodical)
            
            return redirect('view_publication', publication_id=publication.id)
            
    else:
        form = FinishUploadPeriodicalIssueForm(publisher=publisher, uploading_publication=uploading_publication)
    
    return render(request, 'publication/publication_finishing_periodical_upload.html', {'publisher':publisher, 'uploading_publication':uploading_publication, 'form':form})

def finishing_upload_book(request, publisher, uploading_publication):
    if request.method == 'POST':
        form = FinishUploadPeriodicalIssueForm(request.POST, publisher=publisher, uploading_publication=uploading_publication)
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
        form = FinishUploadPeriodicalIssueForm(publisher=publisher, uploading_publication=uploading_publication)
    
    return render(request, 'publication/publication_finishing_book_upload.html', {'publisher':publisher, 'uploading_publication':uploading_publication, 'form':form})


"""

    if request.method == 'POST':

        if 'periodical_submit_button' in request.POST:
            periodical_form = FinishUploadPeriodicalIssueForm(request.POST)
            if periodical_form.is_valid():
                periodical_title = periodical_form.cleaned_data['periodical_title']
                periodical = periodical_form.cleaned_data['periodical']
                issue_name = periodical_form.cleaned_data['title']
                description = periodical_form.cleaned_data['description']

                if not periodical:
                    periodical = Periodical.objects.create(publisher=uploading_publication.publisher, title=periodical_title, created_by=request.user, modified_by=request.user)

                publication = Publication.objects.create(
                    publisher=uploading_publication.publisher,
                    uid=uploading_publication.uid,
                    uploaded_file=uploading_publication.uploaded_file,
                    file_name=uploading_publication.file_name,
                    file_ext=uploading_publication.file_ext,
                    publication_type='periodical',
                    publish_status=Publication.PUBLISH_STATUS_UNPUBLISHED,
                    uploaded_by=request.user,
                    modified_by=request.user,
                )

                issue = PeriodicalIssue.objects.create(
                    publication=publication,
                    periodical=periodical,
                )

                uploading_publication.delete()

                return redirect('view_publication', publication_id=publication.id)

        else:
            periodical_form = FinishUploadPeriodicalIssueForm()

        if 'book_submit_button' in request.POST:
            book_form = FinishUploadBookForm(request.POST)
            if book_form.is_valid():
                pass
        else:
            book_form = FinishUploadBookForm()
        
        
        # if 'picture_submit_button' in request.POST:
        #     picture_form = FinishUploadPictureForm(request.POST)
        #     if picture_form.is_valid():
        #         pass
        # else:
        #     picture_form = FinishUploadPictureForm()
        
    else:
        periodical_form = FinishUploadPeriodicalIssueForm()
        book_form = FinishUploadBookForm()
        # picture_form = FinishUploadPictureForm()
    
    return render(request, 'publication/publication_finish_upload.html', {'uploading_publication':uploading_publication, 
        'book_form':book_form, 
        'periodical_form':periodical_form, 
        #'picture_form':picture_form,
        })
"""

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
        data = cache.get(cache_key)
        return HttpResponse(simplejson.dumps(data))
    else:
        return HttpResponseServerError('Server Error: You must provide X-Progress-ID header or query param.')

@login_required
def view_publication(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    publisher = publication.publisher
    return render(request, 'publication/publication_view.html', {'publisher':publisher, 'publication':publication})

@login_required
def download_publication(request, publication_id):
    
    return HttpResponse(publication_id)

@login_required
def get_publication(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)
    
    return private_files_get_file(request, 'publication', 'Publication', 'uploaded_file', str(publication.id), 'sample.pdf')

@login_required
def edit_publication(request, publication_id):
    publication = get_object_or_404(Publication, uid=publication_uid)

    # 

    return render(request, 'publication/publication_edit.html', {'publication':publication})

# Publisher Periodicals ######################################################################

@login_required
def view_publisher_periodicals(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    periodicals = Periodical.objects.filter(publisher=publisher).order_by('-created')

    for periodical in periodicals:
        periodical.published_count = PeriodicalIssue.objects.filter(periodical=periodical, publication__publish_status=Publication.PUBLISH_STATUS_PUBLISHED).count()

        try:
            periodical.last_published = PeriodicalIssue.objects.filter(periodical=periodical, publication__publish_status=Publication.PUBLISH_STATUS_PUBLISHED).latest('publication__published')
        except PeriodicalIssue.DoesNotExist:
            periodical.last_published = None
        
        periodical.outstanding = {
            'ready': PeriodicalIssue.objects.filter(periodical=periodical, publication__publish_status=Publication.PUBLISH_STATUS_READY_TO_PUBLISH).count(),
            'scheduled': PeriodicalIssue.objects.filter(periodical=periodical, publication__publish_status=Publication.PUBLISH_STATUS_SCHEDULE_TO_PUBLISH).count(),
            'unpublished': PeriodicalIssue.objects.filter(periodical=periodical, publication__publish_status=Publication.PUBLISH_STATUS_UNPUBLISHED).count(),
        }

    publications = {
        'ready': Publication.objects.filter(publisher=publisher, publish_status=Publication.PUBLISH_STATUS_READY_TO_PUBLISH),
        'scheduled': Publication.objects.filter(publisher=publisher, publish_status=Publication.PUBLISH_STATUS_SCHEDULE_TO_PUBLISH),
        'unpublished': Publication.objects.filter(publisher=publisher, publish_status=Publication.PUBLISH_STATUS_UNPUBLISHED),
        'unknown': UploadingPublication.objects.filter(publisher=publisher),
    }

    return render(request, 'publication/periodicals.html', {'publisher':publisher, 'periodicals':periodicals, 'publications':publications})

@login_required
def create_publisher_periodical(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if request.method == 'POST':
        form = PublisherPeriodicalForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']

            Periodical.objects.create(publisher=publisher, title=title, description=description, created_by=request.user)
            
            return redirect('view_publisher_periodicals', publisher_id=publisher.id)

    else:
        form = PublisherPeriodicalForm()

    return render(request, 'publication/periodicals_create.html', {'publisher':publisher, 'form':form})

@login_required
def view_periodical(request, periodical_id):
    periodical = get_object_or_404(Periodical, pk=periodical_id)
    publisher = periodical.publisher

    periodical.issues = PeriodicalIssue.objects.filter(periodical=periodical).order_by('publication__uploaded')

    return render(request, 'publication/periodical.html', {'publisher':publisher, 'periodical':periodical})

@login_required
def edit_periodical(request, periodical_id):
    periodical = get_object_or_404(Periodical, pk=periodical_id)
    publisher = periodical.publisher

    if request.method == 'POST':
        form = PublisherPeriodicalForm(request.POST)
        if form.is_valid():
            periodical.title = form.cleaned_data['title']
            periodical.description = form.cleaned_data['description']

            periodical.save()

            return redirect('view_periodical', periodical_id=periodical.id)

    else:
        form = PublisherPeriodicalForm(initial={'title':periodical.title, 'description':periodical.description})
    
    return render(request, 'publication/periodical_edit.html', {'publisher':publisher, 'periodical':periodical, 'form':form})

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
            periodical_title = form.cleaned_data['periodical_title'].strip()
            periodical = form.cleaned_data['periodical']
            issue_name = form.cleaned_data['issue_name'].strip()
            description = form.cleaned_data['description'].strip()

            uploading_publication = UploadingPublication.objects.get(uid=publication_uid)

            if periodical_title:
                periodical = Periodical.objects.create(publisher=publisher, title=periodical_title, created_by=request.user, modified_by=request.user,)

            publication = Publication.objects.create(
                uid=publication_uid,
                file_path='%d/%s.%s' % (publisher.id, publication_uid, uploading_publication.file_ext),
                file_ext=uploading_publication.file_ext,
                publication_type='',
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



# Publisher Books ######################################################################

@login_required
def view_publisher_books(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    return render(request, 'publication/books.html', {'publisher':publisher, })

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
def view_publisher_management(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    return render(request, 'publication/publisher_manage.html', {'publisher':publisher, })

@login_required
def view_publisher_profile(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if request.method == 'POST':
        form = PublisherProfileForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name'].strip()

            publisher.name = name
            publisher.save()

            return redirect('view_publisher_management', publisher_id=publisher.id)

    else:
        form = PublisherProfileForm(initial={'name':publisher.name})
    
    return render(request, 'publication/publisher_manage_profile.html', {'publisher':publisher, 'form':form})

@login_required
def view_publisher_shelfs(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    return render(request, 'publication/publisher_manage_shelfs.html', {'publisher':publisher, })

@login_required
def view_publisher_shelfs_create(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if request.method == 'POST':
        form = PublisherShelfForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']

            PublisherShelf.objects.create(publisher=publisher, name=name, description=description, created_by=request.user)

            # TODO: Message

            return redirect('view_publisher_management', publisher_id=publisher.id)

    else:
        form = PublisherShelfForm()

    return render(request, 'publication/publisher_manage_shelfs_create.html', {'publisher':publisher, 'form':form})

@login_required
def view_publisher_users(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    return render(request, 'publication/publisher_manage_users.html', {'publisher':publisher, })

@login_required
def view_publisher_users_add(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    return render(request, 'publication/publisher_manage_users_add.html', {'publisher':publisher, })

@login_required
def view_publisher_billing(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    return render(request, 'publication/publisher_manage_billing.html', {'publisher':publisher, })    



