# -*- encoding: utf-8 -*-

import os
import datetime

from django.conf import settings
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
    
    if not can(request.user, 'view', publisher):
        raise Http404
        
    if can(request.user, 'edit', publisher):
        recent_publications = Publication.objects.filter(publisher=publisher).order_by('-uploaded')
    else:
        recent_publications = Publication.objects.filter(publisher=publisher, status=Publication.STATUS['PUBLISHED']).order_by('-uploaded')
    
    return render(request, 'publisher/dashboard.html', {'publisher':publisher, 'recent_publications':recent_publications, 'first_time':first_time})

# Publication ######################################################################

@login_required
def upload_publication(request, publisher_id, module_name=''):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not can(request.user, 'edit', publisher):
        raise Http404

    if request.method == 'POST':
        if not module_name:
            module_name = request.POST.get('module')
        
        module = get_object_or_404(Module, module_name=module_name)

        if not has_module(publisher, module):
            raise Http404
        
        form = module.get_module_object('forms').UploadPublicationForm(request.POST, request.FILES, publisher=publisher)

        if form.is_valid():
            module_input = form.cleaned_data['module']
            publication = form.cleaned_data['publication']

            if not form.valid_file_type():
                return response_json_error('file-type-invalid')

            publication = publisher_functions.upload_publication(request, module_input, publication, publisher)

            if not publication:
                return response_json_error('upload')
            
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
    
    if publication.status != Publication.STATUS['UPLOADED']:
        return redirect('view_publication', publication_id=publication.id)
    
    return views_module.finishing_upload_publication(request, publisher, publication)

@login_required
def cancel_upload_publication(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404
    
    if publication.status != Publication.STATUS['UPLOADED']:
        raise Http404
    
    if request.method == 'POST':
        if 'submit-delete' in request.POST:
            views_module = get_publication_module(publication.publication_type, 'views')
            response = views_module.cancel_upload_publication(request, publisher, publication)
            
            publisher_functions.delete_publication(publication)
            messages.success(request, u'ยกเลิกการอัพโหลดไฟล์เรียบร้อย')
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
    
    if not can(request.user, 'edit', publisher) and publication.status != Publication.STATUS['PUBLISHED']:
        raise Http404
    
    if publication.status == Publication.STATUS['UPLOADED']:
        return redirect('finishing_upload_publication', publication_id=publication.id)
    
    return render(request, 'publisher/%s/publication.html' % publication.publication_type, {'publisher':publisher, 'publication':publication})

@login_required
def download_publication(request, publication_id):
    
    return HttpResponse(publication_id)

@login_required
def get_publication(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)

    if not can(request.user, 'edit', publisher) and publication.status != Publication.STATUS['PUBLISHED']:
        raise Http404
    
    return private_files_get_file(request, 'publication', 'Publication', 'uploaded_file', str(publication.id), 'sample.pdf')

@login_required
def edit_publication(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404
    
    if publication.status == Publication.STATUS['UPLOADED']:
        raise Http404
    
    views_module = get_publication_module(publication.publication_type, 'views')
    return views_module.edit_publication(request, publisher, publication)

@login_required
def edit_publication_status(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404
    
    if publication.status == Publication.STATUS['UPLOADED']:
        raise Http404
    
    if request.method == 'POST':
        form = EditPublicationStatusForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            schedule_date = form.cleaned_data['schedule_date']
            schedule_time = form.cleaned_data['schedule_time']

            if status == 'unpublish':
                publisher_functions.set_publication_unpublished(request, publication)
            
            elif status == 'schedule':
                schedule = datetime.datetime.combine(schedule_date, schedule_time)
                publisher_functions.set_publication_scheduled(request, publication, schedule)
            
            elif status == 'publish':
                publisher_functions.set_publication_published(request, publication)
            
            messages.success(request, u'เปลี่ยนสถานะไฟล์เรียบร้อย')
            return redirect('view_publication', publication.id)

    else:
        # PROCESSING -> 'unpublish', show processing note
        # UNPUBLISHED -> 'unpublish'
        # SCHEDULED -> 'schedule'
        # PROCESSING with SCHEDULED -> 'schedule', show processing note
        # PUBLISHED -> 'publish'
        # PUBLISH WHEN READY -> 'unpublish', show processing note, show publish when ready note

        schedule_date = publication.web_scheduled.date() if publication.web_scheduled else None
        schedule_time = publication.web_scheduled.time() if publication.web_scheduled else None

        is_publish_when_ready = False
        
        if publication.status == Publication.STATUS['UNPUBLISHED']:
            status = 'unpublish'
            is_publish_when_ready = PublicationNotice.objects.filter(publication=publication, notice=PublicationNotice.NOTICE['PUBLISH_WHEN_READY']).exists()
        
        elif publication.status == Publication.STATUS['SCHEDULED']:
            status = 'schedule'

        elif publication.status == Publication.STATUS['PUBLISHED']:
            status = 'publish'

        else:
            status = ''
        
        form = EditPublicationStatusForm(initial={'status':status, 'schedule_date':schedule_date, 'schedule_time':schedule_time})

    return render(request, 'publisher/%s/publication_edit_status.html' % publication.publication_type, {'publisher':publisher, 'publication':publication, 'form':form})

@login_required
def replace_publication(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404
    
    if publication.status == Publication.STATUS['UPLOADED']:
        raise Http404
    
    return render(request, 'publisher/publication_replace.html', {'publisher':publisher, 'publication':publication})

@login_required
def delete_publication(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404
    
    if request.method == 'POST':
        deleted = 'submit-delete' in request.POST

        if deleted:
            views_module = get_publication_module(publication.publication_type, 'views')
            response = views_module.delete_publication(request, deleted, publisher, publication)

            publisher_functions.delete_publication(publication)
        
            messages.success(request, u'ลบไฟล์เรียบร้อย')
            return response

        else:
            return redirect('view_publication', publication_id=publication.id)
    
    return render(request, 'publisher/%s/publication_delete.html' % publication.publication_type, {'publisher':publisher, 'publication':publication})

@login_required
def set_publication_published(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404

    if request.method == 'POST' and request.is_ajax():
        if publication.status == Publication.STATUS['UPLOADED']:
            return response_json_error('invalid-status')
        
        if publication.status == Publication.STATUS['PUBLISHED']:
            return response_json_error('published')
        
        publisher_functions.set_publication_published(request, publication)

        return response_json()
    else:
        raise Http404

@login_required
def set_publication_schedule(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404

    if request.method == 'POST' and request.is_ajax():
        if publication.status == Publication.STATUS['UPLOADED']:
            return response_json_error('invalid-status')
        
        try:
            (s_year, s_month, s_day) = request.POST.get('schedule_date').split('-')
            (s_year, s_month, s_day) = (int(s_year), int(s_month), int(s_day))
            (s_hour, s_minute) = request.POST.get('schedule_time').split(':')
            (s_hour, s_minute) = (int(s_hour), int(s_minute))

            schedule = datetime.datetime(s_year, s_month, s_day, s_hour, s_minute, 0)

        except:
            return response_json_error('invalid-schedule')
        
        if schedule <= datetime.datetime.today():
            return response_json_error('past')
        
        publisher_functions.set_publication_scheduled(request, publication, schedule)
        
        return response_json()
    else:
        raise Http404

@login_required
def set_publication_cancel_schedule(request, publication_id):
    publication = get_object_or_404(Publication, id=publication_id)
    publisher = publication.publisher

    if not can(request.user, 'edit', publisher):
        raise Http404

    if request.method == 'POST' and request.is_ajax():
        if not publication.status in (Publication.STATUS['UNPUBLISHED'], Publication.STATUS['PUBLISHED']):
            return response_json_error('invalid-status')
        
        publisher_functions.set_publication_scheduled_cancel(request, publication)
        
        return response_json()
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

            messages.success(request, u'แก้ไขข้อมูลสำนักพิมพ์เรียบร้อย')

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

    for publisher_shelve in publisher_shelves:
        publisher_shelve.count = PublicationShelf.objects.filter(shelf=publisher_shelve).count()
    
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

            messages.success(request, u'สร้างชั้นหนังสือเรียบร้อย')

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

            messages.success(request, u'แก้ไขชั้นหนังสือเรียบร้อย')

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
            messages.success(request, u'ลบชั้นหนังสือเรียบร้อย')
            
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
                    messages.success(request, u'ส่งคำขอถึงผู้ใช้เรียบร้อย')
                else:
                    messages.error(request, u'ไม่สามารถส่งคำขอถึงผู้ใช้ได้')
                
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
                messages.success(request, u'ส่งคำขอถึงผู้ใช้เรียบร้อย')
            else:
                messages.error(request, u'ไม่สามารถส่งคำขอถึงผู้ใช้ได้')
            
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
            messages.success(request, u'ยกเลิกคำขอเรียบร้อย')
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

            messages.success(request, u'แก้ไขข้อมูลผู้ใช้เรียบร้อย')

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
            messages.success(request, u'ถอดผู้ใช้ออกจากทีมเรียบร้อย')
        return redirect('view_publisher_users', publisher_id=publisher.id)

    return render(request, 'publisher/manage/publisher_manage_user_remove.html', {'publisher':publisher, 'user_publisher':user_publisher})

# Billing

@login_required
def view_publisher_billing(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if not can(request.user, 'manage', publisher):
        raise Http404

    return render(request, 'publisher/manage/publisher_manage_billing.html', {'publisher':publisher, })    
