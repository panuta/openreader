# -*- encoding: utf-8 -*-

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST
from django.utils import simplejson

from common.shortcuts import response_json_success
from common.utilities import generate_random_username

from document.models import Publication, OrganizationShelf

from forms import *
from models import *

def auth_login(request):
    from django.contrib.auth.views import login
    return login(request, authentication_form=EmailAuthenticationForm)

@require_GET
@login_required
def view_user_home(request):
    if request.user.is_superuser:
        return redirect('/management/')
    
    user_organizations = UserOrganization.objects.filter(user=request.user, is_active=True).order_by('-is_default', 'created')
    if user_organizations:
        user_organization = user_organizations[0]
    else:
        return redirect('view_user_welcome')
    
    return redirect('view_organization_front', organization_slug=user_organization.organization.slug)

@require_GET
@login_required
def view_user_welcome(request):
    if not UserOrganization.objects.filter(user=request.user, is_active=True).count():
        raise Http404
    
    return render(request, 'accounts/user_welcome.html', {})

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

@require_GET
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

@require_GET
@login_required
def view_organization_profile(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'view_organization', organization):
        raise Http404

    statistics = {
        'publication_count': Publication.objects.filter(organization=organization).count(),
        'shelf_count': OrganizationShelf.objects.filter(organization=organization).count()
    }
    
    return render(request, 'accounts/manage/organization_profile.html', {'organization':organization, 'statistics':statistics})

# Organization Users

@require_GET
@login_required
def view_organization_users(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'view_organization', organization):
        raise Http404
    
    organization_users = UserOrganization.objects.filter(organization=organization, is_active=True).order_by('user__userprofile__first_name', 'user__userprofile__last_name')
    return render(request, 'accounts/manage/organization_users.html', {'organization':organization, 'organization_users':organization_users})

@require_GET
@login_required
def view_organization_invited_users(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'manage_user', organization):
        raise Http404

    invited_users = UserOrganizationInvitation.objects.filter(organization=organization)
    return render(request, 'accounts/manage/organization_users_invited.html', {'organization':organization, 'invited_users':invited_users})

@login_required
def invite_organization_user(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'manage_user', organization):
        raise Http404

    if request.method == 'POST':
        form = InviteOrganizationUserForm(organization, request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            admin_permissions = form.cleaned_data['admin_permissions']
            groups = form.cleaned_data['groups']

            invitation = UserOrganizationInvitation.objects.create_invitation(email, organization, admin_permissions, groups, request.user)
            invitation.send_invitation_email()

            messages.success(request, u'ส่งคำขอเพิ่มผู้ใช้เรียบร้อย รอผู้ใช้ยืนยันคำขอ')
            return redirect('view_organization_invited_users', organization_slug=organization.slug)

    else:
        form = InviteOrganizationUserForm(organization)

    return render(request, 'accounts/manage/organization_user_invite.html', {'organization':organization, 'form':form})

@login_required
def edit_user_invitation(request, invitation_id):
    invitation = get_object_or_404(UserOrganizationInvitation, pk=invitation_id)
    organization = invitation.organization

    if not can(request.user, 'manage_user', organization):
        raise Http404

    if request.method == 'POST':
        form = UpdateOrganizationUserInviteForm(organization, request.POST)
        if form.is_valid():
            invitation.admin_permissions = form.cleaned_data['admin_permissions']

            invitation.groups.clear()
            for group in form.cleaned_data['groups']:
                UserOrganizationInvitationUserGroup.objects.create(invitation=invitation, group=group)
            
            messages.success(request, u'แก้ไขข้อมูลคำขอเรียบร้อยแล้ว')
            return redirect('view_organization_invited_users', organization_slug=organization.slug)

    else:
        form = UpdateOrganizationUserInviteForm(organization, initial={'admin_permissions':invitation.admin_permissions.all(), 'groups':invitation.groups.all()})

    return render(request, 'accounts/manage/organization_user_invite_edit.html', {'organization':organization, 'invitation':invitation, 'form':form})

@require_POST
@login_required
def ajax_resend_user_invitation(request, invitation_id):

    invitation = get_object_or_404(UserOrganizationInvitation, pk=invitation_id)
    organization = invitation.organization

    if not can(request.user, 'manage_user', organization):
        raise Http404
    
    invitation.send_invitation_email()
    
    messages.success(request, u'ส่งคำขอถึงผู้ใช้เรียบร้อย')
    return response_json_success({'redirect_url':reverse('view_organization_invited_users', args=[organization.slug])})

@require_POST
@login_required
def ajax_cancel_user_invitation(request, invitation_id):
    invitation = get_object_or_404(UserOrganizationInvitation, pk=invitation_id)
    organization = invitation.organization

    if not can(request.user, 'manage_user', organization):
        raise Http404

    invitation.delete()

    messages.success(request, u'เพิกถอนคำขอเรียบร้อย')
    return response_json_success({'redirect_url':reverse('view_organization_invited_users', args=[organization.slug])})

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

            UserProfile.objects.create(user=user, email=invitation.email, first_name=first_name, last_name=last_name, web_access=True)

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

    if not can(request.user, 'manage_user', organization):
        raise Http404
    
    if request.method == 'POST':
        form = EditOrganizationUserForm(organization, request.POST)
        if form.is_valid():
            user_organization.admin_permissions.clear()
            for admin_permission in form.cleaned_data['admin_permissions']: user_organization.admin_permissions.add(admin_permission)
            
            user_organization.user.is_staff = len(form.cleaned_data['admin_permissions']) > 0
            user_organization.user.save()

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
        form = EditOrganizationUserForm(organization, initial={'admin_permissions':user_organization.admin_permissions.all(), 'groups':user_organization.groups.all()})

    return render(request, 'accounts/manage/organization_user_edit.html', {'organization':organization, 'user_organization':user_organization, 'form':form})

@require_POST
@login_required
def ajax_remove_organization_user(request, organization_user_id):

    user_organization = get_object_or_404(UserOrganization, pk=organization_user_id)
    organization = user_organization.organization

    if not can(request.user, 'manage_user', organization):
        raise Http404

    user_organization.is_active = False
    user_organization.save()

    messages.success(request, u'ถอดผู้ใช้ออกจากบริษัทเรียบร้อย')
    return response_json_success({'redirect_url':reverse('view_organization_users', args=[organization.slug])})

# Organization Groups

@require_GET
@login_required
def view_organization_groups(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'view_organization', organization):
        raise Http404
    
    organization_groups = OrganizationGroup.objects.filter(organization=organization).order_by('name')

    for group in organization_groups:
        group.user_counter = UserGroup.objects.filter(group=group).count()

    return render(request, 'accounts/manage/organization_groups.html', {'organization':organization, 'organization_groups':organization_groups})

@login_required
def add_organization_group(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'manage_group', organization):
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

    if not can(request.user, 'manage_group', organization):
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

@require_POST
@login_required
def ajax_remove_organization_group(request, organization_group_id):
    group = get_object_or_404(OrganizationGroup, pk=organization_group_id)
    organization = group.organization

    if not can(request.user, 'manage_group', organization):
        raise Http404

    UserGroup.objects.filter(group=group).delete()
    group.delete()

    messages.success(request, u'ลบกลุ่มผู้ใช้เรียบร้อย')
    return response_json_success({'redirect_url':reverse('view_organization_groups', args=[organization.slug])})

# AJAX SERVICES
############################################################################################################################################

@require_GET
@login_required
def ajax_query_users(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'view_organization', organization):
        raise Http404
    
    query_string = request.GET.get('q')
    
    if query_string:
        result = []

        app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
        model = models.get_model(app_label, model_name)
        for user_profile in model._default_manager.filter(user__userorganization__organization=organization).filter(Q(first_name__icontains=query_string) | Q(last_name__icontains=query_string)):
            result.append({'name':user_profile.get_fullname(), 'value':str(user_profile.user.id)})
        
        return HttpResponse(simplejson.dumps(result))
    
    raise Http404

@require_GET
@login_required
def ajax_query_groups(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'view_organization', organization):
        raise Http404
    
    result = []
    organization_groups = OrganizationGroup.objects.filter(organization=organization).order_by('name')
    for organization_group in organization_groups:
        result.append([organization_group.id, organization_group.name])
    
    return HttpResponse(simplejson.dumps(result))
