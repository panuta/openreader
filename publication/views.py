import os
import datetime

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import simplejson

from private_files.views import get_file as private_files_get_file

from common.modules import get_publication_module
from common.shortcuts import response_json, response_json_error

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
            # If a user does not set any default publisher, pick the first one
            publisher = UserPublisher.objects.filter(user=request.user).order_by('created')[0]
            return redirect('view_publisher_dashboard', publisher_id=publisher.id)

@login_required
def view_publisher_dashboard(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    print request.user.get_profile().can('view', publisher)

    return render(request, 'publication/dashboard.html', {'publisher':publisher})

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
def upload_publication(request, publisher_id, module_name=''):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if request.method == 'POST':
        try:
            publisher = Publisher.objects.get(id=publisher_id)
        except Publisher.DoesNotExist:
            return response_json_error('publisher-notexist')
        
        if not module_name:
            form = GeneralUploadPublicationForm(request.POST, request.FILES)
        else:
            if not PublisherModule.objects.filter(publisher=publisher, module_name=module_name).exists():
                return response_json_error('module-denied')
            
            forms_module = get_publication_module(module_name, 'forms')
            if forms_module:
                form = forms_module.UploadPublicationForm(request.POST, request.FILES, publisher=publisher)
            else:
                return response_json_error('module-invalid')

        if form.is_valid():
            module = form.cleaned_data['module']
            uploading_file = form.cleaned_data['publication']

            try:
                uploading_publication = publication_functions.upload_publication(request, module, uploading_file, publisher)
            except:
                return response_json_error('upload')
            
            form.persist(uploading_publication)
            
            return response_json({'next_url':reverse('finishing_upload_publication', args=[uploading_publication.id])})

        else:
            return response_json_error('form-input-invalid')
    
    else:
        if not module_name:
            form = GeneralUploadPublicationForm()
        else:
            if not PublisherModule.objects.filter(publisher=publisher, module_name=module_name).exists():
                raise Http404
            
            forms_module = get_publication_module(module_name, 'forms')
            if forms_module:
                form = forms_module.UploadPublicationForm(initial={'module':module_name}, publisher=publisher)
            else:
                raise Http404
        
        return render(request, 'publication/%s/publication_upload.html' % module_name, {'publisher':publisher, 'form':form})

@login_required
def get_upload_progress(request):
    # Return JSON object with information about the progress of an upload.
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
def finishing_upload_publication(request, publication_id):
    uploading_publication = get_object_or_404(UploadingPublication, pk=publication_id)
    publisher = uploading_publication.publisher

    views_module = get_publication_module(uploading_publication.publication_type, 'views')

    if views_module:
        return views_module.finishing_upload_publication(request, publisher, uploading_publication)
    else:
        raise Http404

@login_required
def view_publication(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    publisher = publication.publisher

    views_module = get_publication_module(publication.publication_type, 'views')

    if views_module:
        return views_module.view_publication(request, publisher, publication)
    else:
        raise Http404

@login_required
def download_publication(request, publication_id):
    
    return HttpResponse(publication_id)

@login_required
def get_publication(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)
    
    return private_files_get_file(request, 'publication', 'Publication', 'uploaded_file', str(publication.id), 'sample.pdf')

@login_required
def edit_publication(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if request.method == 'POST':
        form = MagazineIssueForm(request.POST)
        if form.is_valid():
            publication.title = form.cleaned_data['title']
            publication.description = form.cleaned_data['description']
            publication.save()

            return response('view_publication', publication.id)
    else:
        form = MagazineIssueForm(initial={'title':publication.title, 'description':publication.description})

    return render(request, 'publication/magazine/magazine_edit.html', {'publisher':publisher, 'publication':publication, 'form':form})

def edit_publication_status(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if request.method == 'POST':
        form = PublicationStatusForm(request.POST)
        if form.is_valid():
            publication.title = form.cleaned_data['title']
            publication.description = form.cleaned_data['description']
            publication.save()

            return response('view_publication', publication.id)
    else:
        form = PublicationStatusForm(initial={'title':publication.title, 'description':publication.description})

    return render(request, 'publication/publication_edit_status.html', {'publisher':publisher, 'publication':publication, 'form':form})

@login_required
def set_publication_published(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)

    if request.method == 'POST' and request.is_ajax():
        publication.publish_status = Publication.PUBLISH_STATUS_PUBLISHED
        publication.publish_schedule = None
        publication.published = datetime.datetime.today()
        publication.published_by = request.user
        publication.save()

        return HttpResponse('')
    else:
        raise Http404

@login_required
def set_publication_schedule(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)

    if request.method == 'POST' and request.is_ajax():
        if publication.publish_status == Publication.PUBLISH_STATUS_PUBLISHED:
            return HttpResponse(simplejson.dumps({'error':'pubished'}))
        
        datetime_string = request.POST.get('schedule')
        (s_year, s_month, s_day, s_hour, s_minute) = datetime_string.split('-')
        schedule = datetime.datetime(s_year, s_month, s_day, s_hour, s_minute, 0)
        publication.publish_status = Publication.PUBLISH_STATUS_SCHEDULE_TO_PUBLISH
        publication.publish_schedule = schedule
        publication.published_by = request.user
        publication.save()

        return HttpResponse('')
    else:
        raise Http404

@login_required
def set_publication_cancel_schedule(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)

    if request.method == 'POST' and request.is_ajax():
        if publication.publish_status != Publication.PUBLISH_STATUS_SCHEDULE_TO_PUBLISH:
            return HttpResponse(simplejson.dumps({'error':'no-schedule'}))
        
        publication.publish_status = Publication.PUBLISH_STATUS_UNPUBLISHED
        publication.publish_schedule = None
        publication.published_by = None
        publication.save()

        return HttpResponse('')
    else:
        raise Http404

@login_required
def set_publication_revert(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)

    if request.method == 'POST' and request.is_ajax():
        if publication.publish_status != Publication.PUBLISH_STATUS_READY_TO_PUBLISH:
            return HttpResponse(simplejson.dumps({'error':'not-ready'}))
        
        publication.publish_status = Publication.PUBLISH_STATUS_UNPUBLISHED
        publication.publish_schedule = None
        publication.published_by = None
        publication.save()

        return HttpResponse('')
    else:
        raise Http404

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



