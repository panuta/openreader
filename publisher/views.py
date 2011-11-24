# -*- encoding: utf-8 -*-

import os
import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.forms.util import ErrorList
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import simplejson

from private_files.views import get_file as private_files_get_file

from common.modules import get_publication_module, has_module
from common.permissions import can
from common.shortcuts import response_json, response_json_error

from publisher import functions as publisher_functions

from exceptions import *
from forms import *
from models import *

from accounts.forms import EmailAuthenticationForm
from accounts.models import UserPublisher, UserPublisherInvitation

# Publisher Dashboard ######################################################################

@login_required
def view_dashboard(request):
    try:
        user_publisher = UserPublisher.objects.get(user=request.user, is_default=True)
        return redirect('view_publisher_dashboard', publisher_id=user_publisher.publisher.id)
    except UserPublisher.DoesNotExist:
        if UserPublisher.objects.filter(user=request.user).count() == 0:
            return redirect('view_user_welcome')
        else:
            # If a user does not set any default publisher, pick the first one
            user_publisher = UserPublisher.objects.filter(user=request.user).order_by('created')[0]
            return redirect('view_publisher_dashboard', publisher_id=user_publisher.publisher.id)

@login_required
def view_publisher_dashboard(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if request.user.get_profile().is_first_time:
        request.user.get_profile().is_first_time = False
        request.user.get_profile().save()
        first_time = True
    else:
        first_time = False
    
    recent_publications = Publication.objects.filter(publisher=publisher).exclude(publish_status=Publication.PUBLISH_STATUS['UPLOADING']).order_by('-uploaded')[0:10]

    if not can(request.user, 'view', publisher):
        raise Http404
        
    return render(request, 'publisher/dashboard.html', {'publisher':publisher, 'recent_publications':recent_publications, 'first_time':first_time})

@login_required
def update_publisher(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not can(request.user, 'manage', publisher):
        raise Http404

    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():
            publisher_name = form.cleaned_data['name']

            publisher.name = publisher_name
            publisher.modified_by = request.user
            publisher.save()

            # MESSAGE

            return redirect('view_publisher_dashboard', publisher_id=publisher.id)
    else:
        form = PublisherForm(initial=publisher)
    
    return render(request, 'publisher/publisher_update.html', {'form': form})

@login_required
def deactivate_publisher(request, publisher_id):
    pass

# Publication ######################################################################

@login_required
def upload_publication(request, publisher_id, module_name=''):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not can(request.user, 'edit', publisher):
        raise Http404

    if request.method == 'POST':
        if not module_name:
            form = GeneralUploadPublicationForm(request.POST, request.FILES)
        else:
            try:
                module = Module.objects.get(module_name=module_name)
            except Module.DoesNotExist:
                raise Http404
            
            if not has_module(publisher, module):
                raise Http404
            
            form = module.get_module_object('forms').UploadPublicationForm(request.POST, request.FILES, publisher=publisher)
            
        if form.is_valid():
            module_input = form.cleaned_data['module']
            uploading_file = form.cleaned_data['publication']

            try:
                publication = publisher_functions.upload_publication(request, module_input, uploading_file, publisher)
            except:
                # TODO
                import sys
                print sys.exc_info()
                return response_json_error('upload')
            else:
                form.after_upload(request, publication)
            
            return response_json({'next_url':reverse('finishing_upload_publication', args=[publication.id])})

        else:
            return response_json_error('form-input-invalid')
    
    else:
        raise Http404

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
    publication = get_object_or_404(Publication, pk=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404
    
    views_module = get_publication_module(publication.publication_type, 'views')
    
    if publication.publish_status != Publication.PUBLISH_STATUS['UPLOADING']:
        return redirect('view_publication', publication_id=publication.id)

    return views_module.finishing_upload_publication(request, publisher, publication)

@login_required
def cancel_upload_publication(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404
    
    if publication.publish_status != Publication.PUBLISH_STATUS['UPLOADING']:
        raise Http404
    
    if request.method == 'POST':
        if 'submit-delete' in request.POST:
            views_module = get_publication_module(publication.publication_type, 'views')
            response = views_module.cancel_upload_publication(request, publisher, publication)
            
            publisher_functions.delete_uploading_publication(publication)

            return response

        else:
            return redirect('finishing_upload_publication', publication_id=publication.id)
    
    return render(request, 'publisher/publication_upload_cancel.html', {'publisher':publisher, 'publication':publication})

@login_required
def view_publication(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'view', publisher):
        raise Http404

    views_module = get_publication_module(publication.publication_type, 'views')
    return views_module.view_publication(request, publisher, publication)

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

    if not can(request.user, 'edit', publisher):
        raise Http404

    views_module = get_publication_module(publication.publication_type, 'views')
    return views_module.edit_publication(request, publisher, publication)

@login_required
def edit_publication_status(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404

    views_module = get_publication_module(publication.publication_type, 'views')
    return views_module.edit_publication_status(request, publisher, publication)

@login_required
def delete_publication(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404
    
    if request.method == 'POST':
        deleted = 'submit-delete' in request.POST

        views_module = get_publication_module(publication.publication_type, 'views')
        response = views_module.delete_publication(request, deleted, publisher, publication)

        if deleted:
            publisher_functions.delete_uploading_publication(publication)
        
        return response
    
    return render(request, 'publisher/%s/publication_delete.html' % publication.publication_type, {'publisher':publisher, 'publication':publication})

@login_required
def set_publication_published(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404

    if request.method == 'POST' and request.is_ajax():
        if publication.publish_status == Publication.PUBLISH_STATUS['PUBLISHED']:
            return response_json_error('published')

        publication.publish_status = Publication.PUBLISH_STATUS['PUBLISHED']
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
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404

    if request.method == 'POST' and request.is_ajax():
        try:
            (s_year, s_month, s_day) = request.POST.get('schedule_date').split('-')
            (s_year, s_month, s_day) = (int(s_year), int(s_month), int(s_day))
            (s_hour, s_minute) = request.POST.get('schedule_time').split(':')
            (s_hour, s_minute) = (int(s_hour), int(s_minute))
        except:
            return response_json_error('invalid')
        
        schedule = datetime.datetime(s_year, s_month, s_day, s_hour, s_minute, 0)
        publication.publish_status = Publication.PUBLISH_STATUS['SCHEDULED']
        publication.publish_schedule = schedule
        publication.published = None
        publication.published_by = request.user
        publication.save()

        return HttpResponse('')
    else:
        raise Http404

@login_required
def set_publication_cancel_schedule(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404

    if request.method == 'POST' and request.is_ajax():
        if publication.publish_status != Publication.PUBLISH_STATUS['SCHEDULED']:
            return response_json_error('no-schedule')
        
        publication.publish_status = Publication.PUBLISH_STATUS['UNPUBLISHED']
        publication.publish_schedule = None
        publication.published_by = None
        publication.save()

        return HttpResponse('')
    else:
        raise Http404

# Publisher Management ######################################################################

@login_required
def view_publisher_profile(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    publisher_modules = PublisherModule.objects.filter(publisher=publisher, module__module_type='publication').order_by('created')

    statistics = []
    for publisher_module in publisher_modules:
        stats_dict = publisher_module.get_module_object('views').gather_publisher_statistics(request, publisher)
        stats_dict['title'] = publisher_module.module.title
        stats_dict['template'] = 'publisher/%s/snippets/publisher_statistics.html' % publisher_module.module.module_name
        statistics.append(stats_dict)

    return render(request, 'publisher/manage/publisher_manage_profile.html', {'publisher':publisher, 'statistics':statistics})

def edit_publisher_profile(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not can(request.user, 'manage', publisher):
        raise Http404
    
    if request.method == 'POST':
        form = PublisherProfileForm(request.POST)
        if form.is_valid():
            publisher.name = form.cleaned_data['name']
            publisher.save()

            # MESSAGE

            return redirect('view_publisher_profile', publisher_id=publisher.id)

    else:
        form = PublisherProfileForm(initial={'name':publisher.name})
    
    return render(request, 'publisher/manage/publisher_manage_profile_edit.html', {'publisher':publisher, 'form':form})

# Publisher Shelf

@login_required
def view_publisher_shelfs(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not has_module(publisher, 'shelf'):
        raise Http404
    
    publisher_shelves = PublisherShelf.objects.filter(publisher=publisher).order_by('name')
    
    return render(request, 'publisher/manage/publisher_manage_shelfs.html', {'publisher':publisher, 'publisher_shelves':publisher_shelves})

@login_required
def create_publisher_shelf(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not can(request.user, 'manage', publisher) or not has_module(publisher, 'shelf'):
        raise Http404

    if request.method == 'POST':
        form = PublisherShelfForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']

            PublisherShelf.objects.create(publisher=publisher, name=name, description=description, created_by=request.user)

            # MESSAGE

            return redirect('view_publisher_shelfs', publisher_id=publisher.id)

    else:
        form = PublisherShelfForm()

    return render(request, 'publisher/manage/publisher_manage_shelf_modify.html', {'publisher':publisher, 'form':form})

@login_required
def edit_publisher_shelf(request, publisher_shelf_id):
    publisher_shelf = get_object_or_404(PublisherShelf, pk=publisher_shelf_id)
    publisher = publisher_shelf.publisher

    if not can(request.user, 'manage', publisher) or not has_module(publisher, 'shelf'):
        raise Http404

    if request.method == 'POST':
        form = PublisherShelfForm(request.POST)
        if form.is_valid():
            publisher_shelf.name = form.cleaned_data['shelf']
            publisher_shelf.description = form.cleaned_data['description']
            publisher_shelf.save()

            # MESSAGE

            return redirect('view_publisher_shelfs', publisher_id=publisher.id)

    else:
        form = PublisherShelfForm(initial={'name':publisher_shelf.name, 'description':publisher_shelf.description})

    return render(request, 'publisher/manage/publisher_manage_shelf_modify.html', {'publisher':publisher, 'publisher_shelf':publisher_shelf, 'form':form})

@login_required
def delete_publisher_shelf(request, publisher_shelf_id):
    publisher_shelf = get_object_or_404(PublisherShelf, pk=publisher_shelf_id)
    publisher = publisher_shelf.publisher

    if not can(request.user, 'manage', publisher) or not has_module(publisher, 'shelf'):
        raise Http404

    if request.method == 'POST':
        if 'submit-delete' in request.POST:
            publisher_shelf.delete()
            # MESSAGE
        return redirect('view_publisher_shelfs', publisher_id=publisher.id)

    return render(request, 'publisher/manage/publisher_manage_shelf_delete.html', {'publisher':publisher, 'publisher_shelf':publisher_shelf})

# Publisher Users

@login_required
def view_publisher_users(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    publisher_users = UserPublisher.objects.filter(publisher=publisher).order_by('user__userprofile__first_name', 'user__userprofile__last_name')

    if can(request.user, 'manage', publisher):
        invited_users = UserPublisherInvitation.objects.filter(publisher=publisher)
    else:
        invited_users = None
    
    return render(request, 'publisher/manage/publisher_manage_users.html', {'publisher':publisher, 'publisher_users':publisher_users, 'invited_users':invited_users})

@login_required
def invite_publisher_user(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not can(request.user, 'manage', publisher):
        raise Http404
    
    if request.method == 'POST':
        form = InvitePublisherUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']

            if UserPublisherInvitation.objects.filter(user_email=email, publisher=publisher).exists():
                form._errors['email'] = ErrorList([u'ส่งคำขอถึงผู้ใช้คนนี้แล้ว'])

            else:
                existing_users = User.objects.filter(email=email)

                if existing_users:
                    user = existing_users[0]

                    if not UserPublisher.objects.filter(publisher=publisher, user=user).exists():
                        invitation = UserPublisherInvitation.objects.create_invitation(user.email, publisher, role, request.user)
                    else:
                        form._errors['email'] = ErrorList([u'ผู้ใช้เป็นทีมงานในสำนักพิมพ์อยู่แล้ว'])
                        invitation = None
                
                else:
                    invitation = UserPublisherInvitation.objects.create_invitation(email, publisher, role, request.user)
                
                if invitation:
                    invitation.send_invitation_email()
                    # MESSAGE
                else:
                    # MESSAGE
                    pass
                
                return redirect('view_publisher_users', publisher_id=publisher.id)

    else:
        form = InvitePublisherUserForm()

    return render(request, 'publisher/manage/publisher_manage_user_invite.html', {'publisher':publisher, 'form':form})

def resend_publisher_invitation(request, invitation_id):
    invitation = get_object_or_404(UserPublisherInvitation, pk=invitation_id)
    publisher = invitation.publisher

    if not can(request.user, 'manage', publisher):
        raise Http404
    
    if request.method == 'POST':
        if 'submit-send' in request.POST:
            if invitation.send_invitation_email():
                # MESSAGE
                pass
            else:
                pass
                # TODO: SEND ERROR MESSAGE
            
        return redirect('view_publisher_users', publisher_id=publisher.id)

    return render(request, 'publisher/manage/publisher_manage_user_invite_resend.html', {'publisher':publisher, 'invitation':invitation})

def cancel_publisher_invitation(request, invitation_id):
    invitation = get_object_or_404(UserPublisherInvitation, pk=invitation_id)
    publisher = invitation.publisher

    if not can(request.user, 'manage', publisher):
        raise Http404
    
    if request.method == 'POST':
        if 'submit-remove' in request.POST:
            invitation.delete()
            # MESSAGE
        return redirect('view_publisher_users', publisher_id=publisher.id)

    return render(request, 'publisher/manage/publisher_manage_user_invite_cancel.html', {'publisher':publisher, 'invitation':invitation})

def claim_publisher_invitation(request, invitation_key):
    """
    1. already have account, authenticated, owner -> redirect to publisher page
    2. already have account, authenticated, not owner -> let user logout before continue claiming invitation
    3. already have account, not authenticated -> redirect to login page with next url is publisher page
    4. don't have account -> ask for password, authenticate, redirect to publisher page
    """

    invitation = UserPublisherInvitation.objects.validate_invitation(invitation_key)

    if not invitation:
        raise Http404
    
    if request.method == 'POST':
        form = ClaimPublisherUserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password1 = form.cleaned_data['password1']

            invitation = UserPublisherInvitation.objects.validate_invitation(invitation_key)

            user = User.objects.create_user(invitation.user_email, invitation.user_email, password1)
            user_profile = user.get_profile()
            user_profile.first_name = first_name
            user_profile.last_name = last_name
            user_profile.is_publisher = True
            user_profile.save()

            UserPublisherInvitation.objects.claim_invitation(invitation, user, True)
            
            # Automatically log user in
            user = authenticate(email=invitation.user_email, password=password1)
            login(request, user)
            
            # TODO: SEND MESSAGE

            return redirect('view_publisher_dashboard', publisher_id=invitation.publisher.id)

    else:
        existing_users = User.objects.filter(email=invitation.user_email)

        if existing_users:
            user = existing_users[0]
        else:
            user = None

        if request.user.is_authenticated():
            if user and request.user.id == user.id:
                UserPublisherInvitation.objects.claim_invitation(invitation, user)
                
                # TODO: SEND MESSAGE

                return redirect('view_publisher_dashboard', publisher_id=invitation.publisher.id)
            
            return render(request, 'publisher/manage/publisher_manage_user_invite_claim.html', {'invitation':invitation, 'logout_first':True})

        else:
            if user:
                form = EmailAuthenticationForm()

                return render(request, 'publisher/manage/publisher_manage_user_invite_claim.html', {'invitation':invitation, 'form':form, 'login_first':reverse('claim_publisher_invitation', args=[invitation_key])})
            
        form = ClaimPublisherUserForm()
    
    return render(request, 'publisher/manage/publisher_manage_user_invite_claim.html', {'invitation':invitation, 'form':form, 'first_time':True})

@login_required
def edit_publisher_user(request, publisher_user_id):
    user_publisher = get_object_or_404(UserPublisher, pk=publisher_user_id)
    publisher = user_publisher.publisher

    if not can(request.user, 'manage', publisher):
        raise Http404
    
    if request.method == 'POST':
        form = EditPublisherUserForm(request.POST)
        if form.is_valid():
            user_publisher.role = name=form.cleaned_data['role']
            user_publisher.save()

            # MESSAGE

            return redirect('view_publisher_users', publisher_id=publisher.id)

    else:
        form = EditPublisherUserForm(initial={'role':user_publisher.role})

    return render(request, 'publisher/manage/publisher_manage_user_edit.html', {'publisher':publisher, 'user_publisher':user_publisher, 'form':form})

@login_required
def remove_publisher_user(request, publisher_user_id):
    user_publisher = get_object_or_404(UserPublisher, pk=publisher_user_id)
    publisher = user_publisher.publisher

    if not can(request.user, 'manage', publisher):
        raise Http404
    
    if request.method == 'POST':
        if 'submit-delete' in request.POST:
            user_publisher.delete()
            # MESSAGE
        return redirect('view_publisher_users', publisher_id=publisher.id)

    return render(request, 'publisher/manage/publisher_manage_user_remove.html', {'publisher':publisher, 'user_publisher':user_publisher})

# Billing

@login_required
def view_publisher_billing(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not can(request.user, 'manage', publisher):
        raise Http404

    return render(request, 'publisher/manage/publisher_manage_billing.html', {'publisher':publisher, })    
