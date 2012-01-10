# -*- encoding: utf-8 -*-

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse
from django.forms.util import ErrorList
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _

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

def view_organization_profile(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if settings.SITE_TYPE == 'document':
        from document.views import _organization_statistics
        statistics = [_organization_statistics(organization)]
    
    elif settings.SITE_TYPE == 'publisher':
        pass

    return render(request, 'accounts/manage/organization_profile.html', {'organization':organization, 'statistics':statistics})

def edit_organization_profile(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'manage', organization):
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

    if can(request.user, 'manage', organization):
        invited_users = UserOrganizationInvitation.objects.filter(organization=organization)
    else:
        invited_users = None
    
    return render(request, 'accounts/manage/organization_users.html', {'organization':organization, 'organization_users':organization_users, 'invited_users':invited_users})

@login_required
def invite_organization_user(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'manage', organization):
        raise Http404

    if request.method == 'POST':
        form = InviteOrganizationUserForm(organization, request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']

            invitation = UserOrganizationInvitation.objects.create_invitation(email, organization, role, request.user)
            
            if invitation:
                invitation.send_invitation_email()
                messages.success(request, u'ส่งคำขอเพิ่มผู้ใช้เรียบร้อย รอผู้ใช้ยืนยัน')
            else:
                messages.error(request, u'ไม่สามารถส่งคำขอถึงผู้ใช้ได้')

            return redirect('view_organization_users', organization_slug=organization.slug)

    else:
        form = InviteOrganizationUserForm(organization)

    return render(request, 'accounts/manage/organization_user_invite.html', {'organization':organization, 'form':form})

def resend_user_invitation(request, invitation_id):
    invitation = get_object_or_404(UserOrganizationInvitation, pk=invitation_id)
    organization = invitation.organization

    if not can(request.user, 'manage', organization):
        raise Http404
    
    if request.method == 'POST':
        if 'submit-send' in request.POST:
            if invitation.send_invitation_email():
                messages.success(request, u'ส่งคำขอถึงผู้ใช้เรียบร้อย')
            else:
                messages.error(request, u'ไม่สามารถส่งคำขอถึงผู้ใช้ได้')
            
        return redirect('view_organization_users', organization_slug=organization.slug)

    return render(request, 'accounts/manage/organization_user_invite_resend.html', {'organization':organization, 'invitation':invitation})

def cancel_user_invitation(request, invitation_id):
    invitation = get_object_or_404(UserOrganizationInvitation, pk=invitation_id)
    organization = invitation.organization

    if not can(request.user, 'manage', organization):
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

            user = User.objects.create_user(invitation.user_email, invitation.user_email, password1)

            from django.db import models
            app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
            model = models.get_model(app_label, model_name)
            user_profile = model._default_manager.create(user=user, first_name=first_name, last_name=last_name)

            UserOrganizationInvitation.objects.claim_invitation(invitation, user, True)
            
            # Automatically log user in
            user = authenticate(email=invitation.user_email, password=password1)
            login(request, user)
            
            return redirect('view_organization_front', organization_slug=invitation.organization.slug)

    else:
        existing_users = User.objects.filter(email=invitation.user_email)

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

    if not can(request.user, 'manage', organization):
        raise Http404
    
    if request.method == 'POST':
        form = EditOrganizationUserForm(organization, request.POST)
        if form.is_valid():
            user_organization.role = form.cleaned_data['role']
            user_organization.save()

            messages.success(request, u'แก้ไขข้อมูลผู้ใช้เรียบร้อย')

            return redirect('view_organization_users', organization_slug=organization.slug)

    else:
        form = EditOrganizationUserForm(organization, initial={'role':user_organization.role})

    return render(request, 'accounts/manage/organization_user_edit.html', {'organization':organization, 'user_organization':user_organization, 'form':form})

@login_required
def remove_organization_user(request, organization_user_id):
    user_organization = get_object_or_404(UserOrganization, pk=organization_user_id)
    organization = user_organization.organization

    if not can(request.user, 'manage', organization):
        raise Http404
    
    if request.method == 'POST':
        if 'submit-remove' in request.POST:
            user_organization.delete()
            messages.success(request, u'ถอดผู้ใช้ออกจากทีมเรียบร้อย')
        return redirect('view_organization_users', organization_slug=organization.slug)

    return render(request, 'accounts/manage/organization_user_remove.html', {'organization':organization, 'user_organization':user_organization})

# Organization Roles

@login_required
def view_organization_roles(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    organization_roles = OrganizationRole.objects.filter(organization=organization).order_by('-admin_level', 'name')

    if not can(request.user, 'manage', organization):
        raise Http404

    for role in organization_roles:
        role.user_counter = UserOrganization.objects.filter(role=role).count()

    return render(request, 'accounts/manage/organization_roles.html', {'organization':organization, 'organization_roles':organization_roles})

@login_required
def add_organization_role(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'manage', organization):
        raise Http404

    if request.method == 'POST':
        form = OrganizationRoleForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            is_admin = form.cleaned_data['is_admin']

            role = OrganizationRole.objects.create(organization=organization, name=name, description=description, admin_level=OrganizationRole.ADMIN_LEVEL_NORMAL if is_admin else OrganizationRole.ADMIN_LEVEL_NOTHING)

            messages.success(request, u'เพิ่มกลุ่มผู้ใช้เรียบร้อย')
            return redirect('view_organization_roles', organization_slug=organization.slug)

    else:
        form = OrganizationRoleForm()
    
    return render(request, 'accounts/manage/organization_role_modify.html', {'organization':organization, 'form':form})

@login_required
def edit_organization_role(request, organization_role_id):
    role = get_object_or_404(OrganizationRole, pk=organization_role_id)
    organization = role.organization

    if not can(request.user, 'manage', organization):
        raise Http404

    if request.method == 'POST':
        form = OrganizationRoleForm(request.POST)
        if form.is_valid():
            role.name = form.cleaned_data['name']
            role.description = form.cleaned_data['description']
            role.admin_level = OrganizationRole.ADMIN_LEVEL_NORMAL if form.cleaned_data['is_admin'] else OrganizationRole.ADMIN_LEVEL_NOTHING
            role.save()

            messages.success(request, u'แก้ไขกลุ่มผู้ใช้เรียบร้อย')
            return redirect('view_organization_roles', organization_slug=organization.slug)

    else:
        form = OrganizationRoleForm(initial={'name':role.name, 'description':role.description, 'is_admin':role.admin_level==OrganizationRole.ADMIN_LEVEL_NORMAL})
    
    return render(request, 'accounts/manage/organization_role_modify.html', {'organization':organization, 'role':role, 'form':form})

@login_required
def remove_organization_role(request, organization_role_id):
    role = get_object_or_404(OrganizationRole, pk=organization_role_id)
    organization = role.organization

    if not can(request.user, 'manage', organization):
        raise Http404

    role.user_counter = UserOrganization.objects.filter(role=role).count()

    if request.method == 'POST':
        form = RemoveOrganizationRoleForm(organization, role, request.POST)
        if form.is_valid():
            if 'submit-remove' in request.POST:
                new_role = form.cleaned_data['role']

                rows = UserOrganization.objects.filter(role=role).update(role=new_role)
                role.delete()

                if rows:
                    messages.success(request, u'ลบกลุ่มผู้ใช้และย้ายผู้ใช้ไปกลุ่มผู้ใช้ใหม่เรียบร้อย')
                else:
                    messages.success(request, u'ลบกลุ่มผู้ใช้เรียบร้อย')
            
            return redirect('view_organization_roles', organization_slug=organization.slug)

    else:
        form = RemoveOrganizationRoleForm(organization, role)
    
    return render(request, 'accounts/manage/organization_role_remove.html', {'organization':organization, 'role':role, 'form':form})

# Billing

@login_required
def view_organization_billing(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'manage', organization):
        raise Http404

    return render(request, 'accounts/manage/organization_billing.html', {'organization':organization, })    
