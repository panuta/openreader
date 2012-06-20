# -*- encoding: utf-8 -*-

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from private_files.views import get_file as private_files_get_file

from common.shortcuts import response_json_success, response_json_error
from common.utilities import format_abbr_datetime, humanize_file_size

from domain import functions as domain_functions
from domain.models import *

from forms import *

from accounts.permissions import get_backend as get_permission_backend
from domain.tasks import prepare_publication

logger = logging.getLogger(settings.OPENREADER_LOGGER)


@login_required
def view_my_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.user, request.POST)
        if form.is_valid():
            user_profile = request.user.get_profile()
            user_profile.email = form.cleaned_data['email']
            user_profile.first_name = form.cleaned_data['first_name']
            user_profile.last_name = form.cleaned_data['last_name']
            user_profile.save()

            messages.success(request, u'แก้ไขข้อมูลส่วนตัวเรียบร้อย')
            return redirect('view_my_profile')
    else:
        form = UserProfileForm(request.user, initial={
            'email': request.user.email,
            'first_name': request.user.get_profile().first_name,
            'last_name': request.user.get_profile().last_name,
        })

    return render(request, 'accounts/my_profile.html', {'form':form})


@login_required
def change_my_account_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, u'เปลี่ยนรหัสผ่านเรียบร้อย')
            return redirect('view_my_profile')

    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'accounts/my_account_change_password.html', {'form':form})


# Organization Profile
# ----------------------------------------------------------------------------------------------------------------------

@login_required
def view_organization_front(request, organization_slug):
    return redirect('view_documents', organization_slug=organization_slug)


@require_GET
@login_required
def view_organization_profile(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not get_permission_backend(request).can_view_organization(request.user, organization):
        raise Http404

    statistics = {
        'publication_count': Publication.objects.filter(organization=organization).count(),
        'shelf_count': OrganizationShelf.objects.filter(organization=organization).count()
    }

    return render(request, 'organization/organization_profile.html', {'organization':organization, 'statistics':statistics})

# Organization Users
# ----------------------------------------------------------------------------------------------------------------------

@require_GET
@login_required
def view_organization_users_groups(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not get_permission_backend(request).can_manage_user(request.user, organization):
        raise Http404

    organization_users = UserOrganization.objects.filter(organization=organization, is_active=True).order_by('user__userprofile__first_name', 'user__userprofile__last_name')
    organization_groups = OrganizationGroup.objects.filter(organization=organization).order_by('name')

    return render(request, 'organization/organization_manage_users_groups.html', {'organization':organization, 'organization_users':organization_users, 'organization_groups':organization_groups})


# User Invitation

@require_GET
@login_required
def view_organization_invited_users(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not get_permission_backend(request).can_manage_user(request.user, organization):
        raise Http404

    invited_users = UserOrganizationInvitation.objects.filter(organization=organization)
    return render(request, 'organization/organization_users_invited.html', {'organization':organization, 'invited_users':invited_users})


@login_required
def invite_organization_user(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not get_permission_backend(request).can_manage_user(request.user, organization):
        raise Http404

    if request.method == 'POST':
        form = InviteOrganizationUserForm(organization, request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            groups = form.cleaned_data['groups']
            admin_permissions = form.cleaned_data['admin_permissions']

            invitation = UserOrganizationInvitation.objects.create_invitation(email, organization, admin_permissions, groups, request.user)
            invitation.send_invitation_email()

            messages.success(request, u'ส่งคำขอเพิ่มผู้ใช้เรียบร้อย รอผู้ใช้ยืนยันคำขอ')
            return redirect('view_organization_users', organization_slug=organization.slug)

    else:
        form = InviteOrganizationUserForm(organization)

    return render(request, 'organization/organization_user_invite.html', {'organization':organization, 'form':form})


@login_required
def edit_user_invitation(request, invitation_id):
    invitation = get_object_or_404(UserOrganizationInvitation, pk=invitation_id)
    organization = invitation.organization

    if not get_permission_backend(request).can_manage_user(request.user, organization):
        raise Http404

    if request.method == 'POST':
        form = EditOrganizationUserInviteForm(organization, request.POST)
        if form.is_valid():
            invitation.admin_permissions = form.cleaned_data['admin_permissions']
            invitation.groups = form.cleaned_data['groups']

            messages.success(request, u'แก้ไขข้อมูลคำขอเรียบร้อยแล้ว')
            return redirect('view_organization_invited_users', organization_slug=organization.slug)

    else:
        form = EditOrganizationUserInviteForm(organization, initial={'admin_permissions':invitation.admin_permissions.all(), 'groups':invitation.groups.all()})

    return render(request, 'organization/organization_user_invite_edit.html', {'organization':organization, 'invitation':invitation, 'form':form})


def claim_user_invitation(request, invitation_key):
    """
    - Authenticated with different account -> Ask user to logout
    - Found invitation's email in system -> Log user in automatically and claim invitation
    - No invitation's email in system -> User submit registration form
    """

    invitation = get_object_or_404(UserOrganizationInvitation, invitation_key=invitation_key)

    try:
        registered_user = User.objects.get(email=invitation.email)
    except User.DoesNotExist:
        registered_user = None

    # Show logout notice if user is authenticated with different account
    if request.user.is_authenticated() and (not registered_user or (registered_user and registered_user.id != request.user.id)):
        return render(request, 'organization/organization_user_invite_claim.html', {'invitation':invitation, 'logout_first':True})

    # Log user in automatically if invited user is already registered
    if registered_user:
        if not request.user.is_authenticated():
            user = authenticate(invitation_key=invitation.invitation_key)
            login(request, user)

        UserOrganizationInvitation.objects.claim_invitation(invitation, registered_user)
        messages.success(request, u'คุณได้เข้าร่วมเป็นส่วนหนึ่งของ%s %s เรียบร้อยแล้ว' % (invitation.organization.prefix, invitation.organization.name))
        return redirect('view_organization_front', organization_slug=invitation.organization.slug)

    # Require user to submit registration form
    if request.method == 'POST':
        form = ClaimOrganizationUserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password1 = form.cleaned_data['password1']

            user_profile = UserProfile.objects.create_user_profile(invitation.email, first_name, last_name, password1)
            UserOrganizationInvitation.objects.claim_invitation(invitation, user_profile.user, True)

            # Automatically log user in
            user = authenticate(email=invitation.email, password=password1)
            login(request, user)

            messages.success(request, u'คุณได้เข้าร่วมเป็นส่วนหนึ่งของ%s %s เรียบร้อยแล้ว' % (invitation.organization.prefix, invitation.organization.name))
            return redirect('view_organization_front', organization_slug=invitation.organization.slug)

    else:
        form = ClaimOrganizationUserForm()

    return render(request, 'organization/organization_user_invite_claim.html', {'invitation':invitation, 'form':form, 'first_time':True})


@login_required
def edit_organization_user(request, organization_user_id):
    user_organization = get_object_or_404(UserOrganization, pk=organization_user_id)
    organization = user_organization.organization

    if not get_permission_backend(request).can_manage_user(request.user, organization):
        raise Http404

    if request.method == 'POST':
        form = EditOrganizationUserForm(user_organization, request.POST)
        if form.is_valid():
            user_organization.user.email = form.cleaned_data['email']


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

            next = request.POST.get('next')
            
            return redirect(next) if next else redirect('view_organization_users', organization_slug=organization.slug)

    else:
        form = EditOrganizationUserForm(user_organization, initial={
            'email'             :user_organization.user.email,
            'first_name'        :user_organization.user.get_profile().first_name,
            'last_name'         :user_organization.user.get_profile().last_name,
            'admin_permissions' :user_organization.admin_permissions.all(),
            'groups'            :user_organization.groups.all()}
        )

    return render(request, 
        'organization/organization_user_edit.html', {
            'form'              :form,
            'organization'      :organization, 
            'user_organization' :user_organization, 
            'next'              :request.GET.get('next', ''),
        }
    )


# Organization Groups
# ----------------------------------------------------------------------------------------------------------------------

@login_required
def add_organization_group(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not get_permission_backend(request).can_manage_group(request.user, organization):
        raise Http404

    if request.method == 'POST':
        form = OrganizationGroupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']

            OrganizationGroup.objects.create(organization=organization, name=name, description=description)

            messages.success(request, u'เพิ่มกลุ่มผู้ใช้เรียบร้อย')
            return redirect('view_organization_groups', organization_slug=organization.slug)

    else:
        form = OrganizationGroupForm()

    return render(request, 'organization/organization_group_modify.html', {'organization':organization, 'form':form})

@login_required
def view_organization_group_members(request, organization_group_id):
    group = get_object_or_404(OrganizationGroup, pk=organization_group_id)
    organization = group.organization

    if not get_permission_backend(request).can_manage_user(request.user, organization):
        raise Http404

    group_members = UserGroup.objects.filter(group=group)
    return render(request, 'organization/organization_group_members.html', {
        'organization': organization, 
        'group' :group,
        'group_members': group_members
    })

@login_required
def edit_organization_group(request, organization_group_id):
    group = get_object_or_404(OrganizationGroup, pk=organization_group_id)
    organization = group.organization

    if not get_permission_backend(request).can_manage_group(request.user, organization):
        raise Http404

    if request.method == 'POST':
        form = OrganizationGroupForm(request.POST)
        if form.is_valid():
            group.name = form.cleaned_data['name']
            group.description = form.cleaned_data['description']
            group.save()

            messages.success(request, u'แก้ไขกลุ่มผู้ใช้เรียบร้อย')
            return redirect('view_organization_groups', organization_slug=organization.slug)

    else:
        form = OrganizationGroupForm(initial={'name':group.name, 'description':group.description})

    return render(request, 'organization/organization_group_modify.html', {'organization':organization, 'group':group, 'form':form})


# Publication
########################################################################################################################

@require_GET
@login_required
def view_documents(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not get_permission_backend(request).can_view_organization(request.user, organization):
        raise Http404

    shelves = get_permission_backend(request).get_viewable_shelves(request.user, organization)
    uploadable_shelves = get_permission_backend(request).get_uploadable_shelves(request.user, organization)
    recent_publications = Publication.objects.filter(organization=organization).order_by('-uploaded')[:10]
    return render(request, 'document/documents.html', {'organization':organization, 'shelves':shelves, 'uploadable_shelves':uploadable_shelves, 'recent_publications':recent_publications})


@require_GET
@login_required
def view_documents_by_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, pk=shelf_id)

    if shelf.organization.id != organization.id or not get_permission_backend(request).can_view_shelf(request.user, organization, {'shelf':shelf}):
        raise Http404

    uploadable_shelves = get_permission_backend(request).get_uploadable_shelves(request.user, organization)
    publications = Publication.objects.filter(organization=organization, shelves__in=[shelf]).order_by('-uploaded')
    return render(request, 'document/documents_shelf.html', {'organization':organization, 'publications':publications, 'shelf':shelf, 'uploadable_shelves':uploadable_shelves})


@require_GET
@login_required
def download_publication(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)

    if not get_permission_backend(request).can_view_publication(request.user, publication.organization, {'publication':publication}):
        raise Http404

    return private_files_get_file(request, 'domain', 'Publication', 'uploaded_file', str(publication.id), '%s.%s' % (publication.original_file_name, publication.file_ext))


# SHELF
# ----------------------------------------------------------------------------------------------------------------------

def _persist_shelf_permissions(request, organization, shelf):
    OrganizationShelfPermission.objects.filter(shelf=shelf).delete()
    GroupShelfPermission.objects.filter(shelf=shelf).delete()
    UserShelfPermission.objects.filter(shelf=shelf).delete()

    for permission in request.POST.getlist('permission'):
        permit = permission.split('-')

        if permit[0] == 'all':
            OrganizationShelfPermission.objects.create(shelf=shelf, access_level=int(permit[1]), created_by=request.user)

        elif permit[0] == 'group':
            group = get_object_or_404(OrganizationGroup, pk=int(permit[1]))
            GroupShelfPermission.objects.create(shelf=shelf, group=group, access_level=int(permit[2]), created_by=request.user)

        elif permit[0] == 'user':
            user = get_object_or_404(User, pk=int(permit[1]))
            UserShelfPermission.objects.create(shelf=shelf, user=user, access_level=int(permit[2]), created_by=request.user)


def _extract_shelf_permissions(shelf):
    shelf_permissions = []

    try:
        organization_shelf_permission = OrganizationShelfPermission.objects.get(shelf=shelf)
        shelf_permissions.append('all-%d' % organization_shelf_permission.access_level)
    except:
        pass

    for shelf_permission in GroupShelfPermission.objects.filter(shelf=shelf):
        shelf_permissions.append('group-%d-%d' % (shelf_permission.group.id, shelf_permission.access_level))

    for shelf_permission in UserShelfPermission.objects.filter(shelf=shelf):
        shelf_permissions.append('user-%d-%d' % (shelf_permission.user.id, shelf_permission.access_level))

    return shelf_permissions


@login_required
def create_document_shelf(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not get_permission_backend(request).can_manage_shelf(request.user, organization):
        raise Http404

    if request.method == 'POST':
        form = OrganizationShelfForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            auto_sync = form.cleaned_data['auto_sync']
            shelf_icon = form.cleaned_data['shelf_icon']
            permissions = request.POST.getlist('permission')

            shelf = OrganizationShelf.objects.create(organization=organization, name=name, auto_sync=auto_sync, icon=shelf_icon, created_by=request.user)

            _persist_shelf_permissions(request, organization, shelf)

            messages.success(request, u'สร้างชั้นหนังสือเรียบร้อย')
            return redirect('view_documents_by_shelf', organization_slug=organization.slug, shelf_id=shelf.id)

        shelf_permissions = request.POST.getlist('permission')

    else:
        form = OrganizationShelfForm(initial={'shelf_icon':settings.DEFAULT_SHELF_ICON})
        shelf_permissions = ['all-1']

    return render(request, 'document/shelf_modify.html', {'organization':organization, 'form':form, 'shelf':None, 'shelf_type':'create', 'shelf_permissions':shelf_permissions})


@login_required
def edit_document_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, pk=shelf_id)

    if shelf.organization.id != organization.id or not get_permission_backend(request).can_manage_shelf(request.user, organization):
        raise Http404

    if request.method == 'POST':
        form = OrganizationShelfForm(request.POST)
        if form.is_valid():
            shelf.name = form.cleaned_data['name']
            shelf.auto_sync = form.cleaned_data['auto_sync']
            shelf.icon = form.cleaned_data['shelf_icon']
            shelf.save()

            _persist_shelf_permissions(request, organization, shelf)

            messages.success(request, u'แก้ไขชั้นหนังสือเรียบร้อย')
            return redirect('view_documents_by_shelf', organization_slug=organization.slug, shelf_id=shelf.id)

        shelf_permissions = request.POST.getlist('permission')

    else:
        form = OrganizationShelfForm(initial={'name':shelf.name, 'auto_sync':shelf.auto_sync, 'shelf_icon':shelf.icon})
        shelf_permissions = _extract_shelf_permissions(shelf)

    return render(request, 'document/shelf_modify.html', {'organization':organization, 'form':form, 'shelf':shelf, 'shelf_type':'edit', 'shelf_permissions':shelf_permissions})


@login_required
def delete_document_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, pk=shelf_id)

    if shelf.organization.id != organization.id or not get_permission_backend(request).can_manage_shelf(request.user, organization):
        raise Http404

    if request.method == 'POST':
        print request.POST
        if 'submit-delete' in request.POST:
            to_delete_documents = request.POST.get('delete_documents') == 'on'

            if to_delete_documents:
                for publication in Publication.objects.filter(shelves__in=[shelf]):
                    domain_functions.delete_publication(publication)

                messages.success(request, u'ลบชั้นหนังสือและไฟล์ในชั้นเรียบร้อย')

            else:
                messages.success(request, u'ลบชั้นหนังสือเรียบร้อย')

            PublicationShelf.objects.filter(shelf=shelf).delete()
            OrganizationShelfPermission.objects.filter(shelf=shelf).delete()
            GroupShelfPermission.objects.filter(shelf=shelf).delete()
            UserShelfPermission.objects.filter(shelf=shelf).delete()
            shelf.delete()

            return redirect('view_documents', organization_slug=organization.slug)

        else:
            return redirect('view_documents_by_shelf', organization_slug=organization.slug, shelf_id=shelf.id)

    shelf_documents_count = Publication.objects.filter(shelves__in=[shelf]).count()
    return render(request, 'document/shelf_delete.html', {'organization':organization, 'shelf_documents_count':shelf_documents_count, 'shelf':shelf, 'shelf_type':'delete'})
