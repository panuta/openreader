# -*- encoding: utf-8 -*-

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.forms.util import ErrorList
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

from openreader.http import Http403

from common.utilities import generate_random_username

from document.models import Publication, OrganizationShelf

from forms import *
from models import *

def auth_login(request):
    from django.contrib.auth.views import login
    return login(request, authentication_form=EmailAuthenticationForm)

@login_required
def view_user_home(request):
    if request.user.is_superuser:
        return redirect('/management/')
    
    try:
        user_organization = UserOrganization.objects.get(user=request.user, is_default=True)
    except UserOrganization.DoesNotExist:
        if UserOrganization.objects.filter(user=request.user).count() == 0:
            return redirect('view_user_welcome')
        else:
            # If a user does not set any default publisher, pick the first one
            user_organization = UserOrganization.objects.filter(user=request.user).order_by('created')[0]
    
    return redirect('view_organization_front', organization_slug=user_organization.organization.slug)

def view_user_welcome(request):
    if UserOrganization.objects.filter(user=request.user).count() != 0:
        raise Http404
    
    welcome_contact_email = settings.WELCOME_CONTACT_EMAIL
    return render(request, 'accounts/user_welcome.html', {'welcome_contact_email':welcome_contact_email})

@login_required
def view_my_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user_profile = request.user.get_profile()
            user_profile.first_name = form.cleaned_data['first_name']
            user_profile.last_name = form.cleaned_data['last_name']
            user_profile.save()

            messages.success(request, u'แก้ไขข้อมูลส่วนตัวเรียบร้อย')
            return redirect('view_my_profile')
    else:
        form = UserProfileForm(initial=request.user.get_profile().__dict__)

    return render(request, 'accounts/my_profile.html', {'form':form})

@login_required
def view_my_account(request):
    return render(request, 'accounts/my_account.html', {})

@login_required
def change_my_account_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, u'เปลี่ยนรหัสผ่านเรียบร้อย')
            return redirect('view_my_account')

    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'accounts/my_account_change_password.html', {'form':form})

# ORGANIZATION ##############################################################################################################

@login_required
def view_organization_profile(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    statistics = {
        'document_count': Publication.objects.filter(organization=organization).count(),
        'shelf_count': OrganizationShelf.objects.filter(organization=organization).count()
    }
    
    return render(request, 'accounts/manage/organization_profile.html', {'organization':organization, 'statistics':statistics})

@login_required
def edit_organization_profile(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'admin', {'organization':organization}):
        raise Http404
    
    if request.method == 'POST':
        form = OrganizationProfileForm(request.POST)
        if form.is_valid():
            organization.name = form.cleaned_data['name']
            organization.save()

            messages.success(request, u'แก้ไขข้อมูล%sเรียบร้อย' % organization.prefix)
            return redirect('view_organization_profile', organization_slug=organization.slug)

    else:
        form = OrganizationProfileForm(initial={'name':organization.name})
    
    return render(request, 'accounts/manage/organization_profile_edit.html', {'organization':organization, 'form':form})

# Organization Users

@login_required
def view_organization_users(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    organization_users = UserOrganization.objects.filter(organization=organization).order_by('user__userprofile__first_name', 'user__userprofile__last_name')

    if can(request.user, 'admin', {'organization':organization}):
        invited_users = UserOrganizationInvitation.objects.filter(organization=organization)
    else:
        invited_users = None
    
    return render(request, 'accounts/manage/organization_users.html', {'organization':organization, 'organization_users':organization_users, 'invited_users':invited_users})

@login_required
def invite_organization_user(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'admin', {'organization':organization}):
        raise Http404

    if request.method == 'POST':
        form = InviteOrganizationUserForm(organization, request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            position = form.cleaned_data['position']
            is_admin = form.cleaned_data['is_admin']
            groups = form.cleaned_data['groups']

            invitation = UserOrganizationInvitation.objects.create_invitation(email, organization, is_admin, position, groups, request.user)
            
            if invitation:
                invitation.send_invitation_email()
                messages.success(request, u'ส่งคำขอเพิ่มผู้ใช้เรียบร้อย รอผู้ใช้ยืนยัน')
            else:
                messages.error(request, u'ไม่สามารถส่งคำขอถึงผู้ใช้ได้')

            return redirect('view_organization_users', organization_slug=organization.slug)

    else:
        form = InviteOrganizationUserForm(organization)

    return render(request, 'accounts/manage/organization_user_invite.html', {'organization':organization, 'form':form})

@login_required
def view_user_invitation(request, invitation_id):
    invitation = get_object_or_404(UserOrganizationInvitation, pk=invitation_id)
    organization = invitation.organization

    if request.method == 'POST':
        form = UpdateOrganizationUserInviteForm(organization, request.POST)
        if form.is_valid():
            invitation.position = form.cleaned_data['position']
            invitation.is_admin = form.cleaned_data['is_admin']

            invitation.groups.clear()

            for group in form.cleaned_data['groups']:
                UserOrganizationInvitationUserGroup.objects.create(invitation=invitation, group=group)
            
            messages.success(request, u'แก้ไขข้อมูลคำขอเรียบร้อยแล้ว')

            return redirect('view_organization_users', organization_slug=organization.slug)

    else:
        form = UpdateOrganizationUserInviteForm(organization, initial={'position':invitation.position, 'is_admin':invitation.is_admin, 'groups':invitation.groups.all()})

    return render(request, 'accounts/manage/organization_user_invite_details.html', {'organization':organization, 'invitation':invitation, 'form':form})

@login_required
def resend_user_invitation(request, invitation_id):
    invitation = get_object_or_404(UserOrganizationInvitation, pk=invitation_id)
    organization = invitation.organization

    if not can(request.user, 'admin', {'organization':organization}):
        raise Http404
    
    if request.method == 'POST':
        if 'submit-send' in request.POST:
            if invitation.send_invitation_email():
                messages.success(request, u'ส่งคำขอถึงผู้ใช้เรียบร้อย')
            else:
                messages.error(request, u'ไม่สามารถส่งคำขอถึงผู้ใช้ได้')
            
        return redirect('view_organization_users', organization_slug=organization.slug)

    return render(request, 'accounts/manage/organization_user_invite_resend.html', {'organization':organization, 'invitation':invitation})

@login_required
def cancel_user_invitation(request, invitation_id):
    invitation = get_object_or_404(UserOrganizationInvitation, pk=invitation_id)
    organization = invitation.organization

    if not can(request.user, 'admin', {'organization':organization}):
        raise Http404
    
    if request.method == 'POST':
        if 'submit-remove' in request.POST:
            invitation.delete()
            messages.success(request, u'ยกเลิกคำขอเรียบร้อย')
        return redirect('view_organization_users', organization_slug=organization.slug)

    return render(request, 'accounts/manage/organization_user_invite_cancel.html', {'organization':organization, 'invitation':invitation})

def claim_user_invitation(request, invitation_key):
    """
    1. have account, is authenticated, invitation user is matched -> redirect to front page
    2. have account, is authenticated, invitation user is not matched -> ask user to logout
    3. have account, is not authenticated -> ask user to login, redirect to front page after login
    4. don't have account -> fill information, authenticate and redirect to front page after submit
    """

    invitation = UserOrganizationInvitation.objects.validate_invitation(invitation_key)

    if not invitation:
        raise Http404
    
    if request.method == 'POST':
        form = ClaimOrganizationUserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password1 = form.cleaned_data['password1']

            invitation = UserOrganizationInvitation.objects.validate_invitation(invitation_key)

            user = User.objects.create_user(generate_random_username(), '', password1)
            user.username = user.id
            user.save()

            app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
            model = models.get_model(app_label, model_name)
            user_profile = model._default_manager.create(user=user, email=invitation.email, first_name=first_name, last_name=last_name, web_access=True)

            UserOrganizationInvitation.objects.claim_invitation(invitation, user, True)
            
            # Automatically log user in
            user = authenticate(email=invitation.email, password=password1)
            login(request, user)
            
            return redirect('view_organization_front', organization_slug=invitation.organization.slug)

    else:
        existing_users = User.objects.filter(email=invitation.email)

        if existing_users:
            user = existing_users[0]
        else:
            user = None

        if request.user.is_authenticated():
            if user and request.user.id == user.id:
                UserOrganizationInvitation.objects.claim_invitation(invitation, user)
                
                messages.success(request, u'คุณได้เข้าร่วมเป็นส่วนหนึ่งของ%s %s เรียบร้อยแล้ว' % (invitation.organization.prefix, invitation.organization.name))
                return redirect('view_organization_front', organization_slug=invitation.organization.slug)
            
            return render(request, 'accounts/manage/organization_user_invite_claim.html', {'invitation':invitation, 'logout_first':True})

        else:
            if user:
                form = EmailAuthenticationForm()
                return render(request, 'accounts/manage/organization_user_invite_claim.html', {'invitation':invitation, 'form':form, 'login_first':reverse('claim_user_invitation', args=[invitation_key])})
            
        form = ClaimOrganizationUserForm()
    
    return render(request, 'accounts/manage/organization_user_invite_claim.html', {'invitation':invitation, 'form':form, 'first_time':True})

@login_required
def edit_organization_user(request, organization_user_id):
    user_organization = get_object_or_404(UserOrganization, pk=organization_user_id)
    organization = user_organization.organization

    if not can(request.user, 'admin', {'organization':organization}):
        raise Http404
    
    if request.method == 'POST':
        form = EditOrganizationUserForm(organization, request.POST)
        if form.is_valid():
            user_organization.position = form.cleaned_data['position']
            user_organization.is_admin = form.cleaned_data['is_admin']
            user_organization.save()

            new_groups = set()
            for group in form.cleaned_data['groups']:
                new_groups.add(group)
            
            old_groups = set()
            for user_group in UserGroup.objects.filter(user_organization=user_organization):
                old_groups.add(user_group.group)
            
            creating_groups = new_groups.difference(old_groups)
            removing_groups = old_groups.difference(new_groups)

            for group in creating_groups:
                UserGroup.objects.create(group=group, user_organization=user_organization)
            
            UserGroup.objects.filter(user_organization=user_organization, group__in=removing_groups).delete()

            messages.success(request, u'แก้ไขข้อมูลผู้ใช้เรียบร้อย')

            return redirect('view_organization_users', organization_slug=organization.slug)

    else:
        form = EditOrganizationUserForm(organization, initial={'position':user_organization.position, 'is_admin':user_organization.is_admin, 'groups':user_organization.groups.all()})

    return render(request, 'accounts/manage/organization_user_edit.html', {'organization':organization, 'user_organization':user_organization, 'form':form})

@login_required
def remove_organization_user(request, organization_user_id):
    user_organization = get_object_or_404(UserOrganization, pk=organization_user_id)
    organization = user_organization.organization

    if not can(request.user, 'admin', {'organization':organization}):
        raise Http404
    
    if request.method == 'POST':
        if 'submit-remove' in request.POST:
            user_organization.delete()
            messages.success(request, u'ถอดผู้ใช้ออกจากทีมเรียบร้อย')
        return redirect('view_organization_users', organization_slug=organization.slug)

    return render(request, 'accounts/manage/organization_user_remove.html', {'organization':organization, 'user_organization':user_organization})

# Organization Groups

@login_required
def view_organization_groups(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    organization_groups = OrganizationGroup.objects.filter(organization=organization).order_by('name')

    if not can(request.user, 'admin', {'organization':organization}):
        raise Http404

    for group in organization_groups:
        group.user_counter = UserGroup.objects.filter(group=group).count()

    return render(request, 'accounts/manage/organization_groups.html', {'organization':organization, 'organization_groups':organization_groups})

@login_required
def add_organization_group(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'admin', {'organization':organization}):
        raise Http404

    if request.method == 'POST':
        form = OrganizationGroupForm(organization, request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            
            group = OrganizationGroup.objects.create(organization=organization, name=name, description=description)

            for member in form.cleaned_data['members']:
                UserGroup.objects.create(group=group, user_organization=member)

            messages.success(request, u'เพิ่มกลุ่มผู้ใช้เรียบร้อย')
            return redirect('view_organization_groups', organization_slug=organization.slug)

    else:
        form = OrganizationGroupForm(organization)
    
    return render(request, 'accounts/manage/organization_group_modify.html', {'organization':organization, 'form':form})

@login_required
def edit_organization_group(request, organization_group_id):
    group = get_object_or_404(OrganizationGroup, pk=organization_group_id)
    organization = group.organization

    if not can(request.user, 'admin', {'organization':organization}):
        raise Http404

    if request.method == 'POST':
        form = OrganizationGroupForm(organization, request.POST)
        if form.is_valid():
            group.name = form.cleaned_data['name']
            group.description = form.cleaned_data['description']
            group.save()

            new_members = set(form.cleaned_data['members'])
            
            old_members = set()
            for member in UserGroup.objects.filter(group=group):
                old_members.add(member.user_organization)
            
            creating_members = new_members.difference(old_members)
            removing_members = old_members.difference(new_members)

            for member in creating_members:
                UserGroup.objects.create(group=group, user_organization=member)
            
            UserGroup.objects.filter(group=group, user_organization__in=removing_members).delete()

            messages.success(request, u'แก้ไขกลุ่มผู้ใช้เรียบร้อย')
            return redirect('view_organization_groups', organization_slug=organization.slug)

    else:
        members = []
        for member in UserGroup.objects.filter(group=group):
            members.append(member.user_organization)

        form = OrganizationGroupForm(organization, initial={'name':group.name, 'description':group.description, 'members':members})
    
    return render(request, 'accounts/manage/organization_group_modify.html', {'organization':organization, 'group':group, 'form':form})

@login_required
def remove_organization_group(request, organization_group_id):
    group = get_object_or_404(OrganizationGroup, pk=organization_group_id)
    organization = group.organization

    if not can(request.user, 'admin', {'organization':organization}):
        raise Http404

    group.user_counter = UserGroup.objects.filter(group=group).count()

    if request.method == 'POST':
        if 'submit-delete' in request.POST:
            UserGroup.objects.filter(group=group).delete()
            group.delete()

            messages.success(request, u'ลบกลุ่มผู้ใช้เรียบร้อย')
        
        return redirect('view_organization_groups', organization_slug=organization.slug)
    
    return render(request, 'accounts/manage/organization_group_remove.html', {'organization':organization, 'group':group})

# AJAX SERVICES
############################################################################################################################################

@login_required
def ajax_query_users(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'view', {'organization':organization}):
        raise Http403
    
    query_string = request.GET.get('q')
    
    if query_string:
        result = []

        app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
        model = models.get_model(app_label, model_name)
        for user_profile in model._default_manager.filter(user__userorganization__in=[organization]).filter(Q(first_name__icontains=query_string) | Q(last_name__icontains=query_string)):
            #result.append({'userid':str(user_profile.user.id), 'name':user_profile.get_fullname(), 'value':user_profile.get_fullname()})
            result.append({'name':user_profile.get_fullname(), 'value':str(user_profile.user.id)})
        
        # return HttpResponse(simplejson.dumps({'items':result}))
        return HttpResponse(simplejson.dumps(result))
    
    print request.GET
