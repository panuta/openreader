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

from common.extensions import get_extension_template

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
        form = InviteOrganizationUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']

            if UserOrganizationInvitation.objects.filter(user_email=email, organization=organization).exists():
                form._errors['email'] = ErrorList([u'ส่งคำขอถึงผู้ใช้คนนี้แล้ว'])

            else:
                existing_users = User.objects.filter(email=email)

                if existing_users:
                    user = existing_users[0]

                    if not UserOrganization.objects.filter(organization=organization, user=user).exists():
                        invitation = UserOrganizationInvitation.objects.create_invitation(user.email, organization, role, request.user)
                    else:
                        form._errors['email'] = ErrorList([u'ผู้ใช้เป็นทีมงานในสำนักพิมพ์อยู่แล้ว'])
                        invitation = None
                
                else:
                    invitation = UserOrganizationInvitation.objects.create_invitation(email, organization, role, request.user)
                
                if invitation:
                    invitation.send_invitation_email()
                    messages.success(request, u'ส่งคำขอถึงผู้ใช้เรียบร้อย')
                else:
                    messages.error(request, u'ไม่สามารถส่งคำขอถึงผู้ใช้ได้')
                
                return redirect('view_organization_users', organization_slug=organization.slug)

    else:
        form = InviteOrganizationUserForm()
    
    return render(request, get_extension_template('UserInvitationExtension', 'user_invite', 'accounts/manage/organization_user_invite.html'), {'organization':organization, 'form':form})

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
    1. already have account, authenticated, owner -> redirect to publisher page
    2. already have account, authenticated, not owner -> let user logout before continue claiming invitation
    3. already have account, not authenticated -> redirect to login page with next url is publisher page
    4. don't have account -> ask for password, authenticate, redirect to publisher page
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
            user_profile = user.get_profile()
            user_profile.first_name = first_name
            user_profile.last_name = last_name
            user_profile.web_access = True
            user_profile.save()

            UserOrganizationInvitation.objects.claim_invitation(invitation, user, True)
            
            # Automatically log user in
            user = authenticate(email=invitation.user_email, password=password1)
            login(request, user)
            
            # TODO: SEND MESSAGE

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
                
                # TODO: SEND MESSAGE

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
        form = EditOrganizationUserForm(request.POST)
        if form.is_valid():
            user_organization.role = name=form.cleaned_data['role']
            user_organization.save()

            messages.success(request, u'แก้ไขข้อมูลผู้ใช้เรียบร้อย')

            return redirect('view_organization_users', organization_slug=organization.slug)

    else:
        form = EditOrganizationUserForm(initial={'role':user_organization.role})

    return render(request, 'accounts/manage/organization_user_edit.html', {'organization':organization, 'user_organization':user_organization, 'form':form})

@login_required
def remove_organization_user(request, organization_user_id):
    user_organization = get_object_or_404(UserOrganization, pk=organization_user_id)
    organization = user_organization.organization

    if not can(request.user, 'manage', organization):
        raise Http404
    
    if request.method == 'POST':
        if 'submit-delete' in request.POST:
            user_organization.delete()
            messages.success(request, u'ถอดผู้ใช้ออกจากทีมเรียบร้อย')
        return redirect('view_organization_users', organization_slug=organization.slug)

    return render(request, 'accounts/manage/organization_user_remove.html', {'organization':organization, 'user_organization':user_organization})

# Billing

@login_required
def view_organization_billing(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'manage', organization):
        raise Http404

    return render(request, 'accounts/manage/organization_billing.html', {'organization':organization, })    
