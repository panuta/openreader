# -*- encoding: utf-8 -*-

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _

from domain.models import User, UserProfile, Organization, OrganizationAdminPermission, OrganizationGroup, OrganizationInvitation
from presentation.forms import ClaimOrganizationUserAdminForm, ClaimOrganizationExistUserAdminForm

from forms import *

def manage_front(request):
    return redirect('manage_organizations')

@login_required
def manage_organizations(request):
    if not request.user.is_superuser:
        raise Http404
    
    organizations = Organization.objects.all().order_by('name')
    organizations_invited_count = OrganizationInvitation.objects.all().count()
    return render(request, 'manage/manage_organizations.html', {'organizations':organizations, 'organizations_invited_count': organizations_invited_count})


@login_required
def view_organizations_invited(request):
    if not request.user.is_superuser:
        raise Http404

    organizations_invited = OrganizationInvitation.objects.all().order_by('-created')
    return render(request, 'manage/organizations_invited.html', {'organizations_invited': organizations_invited})    

@login_required
def edit_organization_invitation(request, invitation_id):
    if not request.user.is_superuser:
        raise Http404

    invitation = get_object_or_404(OrganizationInvitation, id=invitation_id)

    if request.method == 'POST':
        form = EditOrganizationInvitationForm(invitation, request.POST)
        if form.is_valid():
            invitation.organization_name = form.cleaned_data['organization_name']
            invitation.organization_slug = form.cleaned_data['organization_slug']
            invitation.organization_prefix = form.cleaned_data['organization_prefix']

            invitation.save()
            return redirect('view_organizations_invited')

    else:
        form = EditOrganizationInvitationForm(invitation, initial={
            'organization_name': invitation.organization_name,
            'organization_slug': invitation.organization_slug,
            'organization_prefix': invitation.organization_prefix,
        })

    return render(request, 'manage/organization_invite_edit.html', {'invitation': invitation, 'form':form})

def claim_organization_invitation(request, invitation_key):
    """
    - Authenticated with different account -> Ask user to logout
    - Found invitation's email in system -> Log user in automatically and claim invitation
    - No invitation's email in system -> User submit registration form
    """

    invitation = get_object_or_404(OrganizationInvitation, invitation_key=invitation_key)

    try:
        registered_user = User.objects.get(email=invitation.admin_email)
    except User.DoesNotExist:
        registered_user = None

    # Show logout notice if user is authenticated with different account
    if request.user.is_authenticated() and (not registered_user or (registered_user and registered_user.id != request.user.id)):
        return render(request, 'manage/organization_invite_claim.html', {'invitation':invitation, 'logout_first':True})

    # Log user in automatically if invited user is already registered
    if registered_user and registered_user.get_profile().id_no:
        if not request.user.is_authenticated():
            user = authenticate(invitation_key=invitation.invitation_key)
            login(request, user)

        OrganizationInvitation.objects.claim_invitation(invitation, registered_user)
        messages.success(request, _('You are an administrator of %s successful.') % (invitation.organization_name))
        return redirect('view_organization_front', organization_slug=invitation.organization_slug)

    # Require user to submit registration form
    if request.method == 'POST':
        if registered_user:
            form = ClaimOrganizationExistUserAdminForm(request.POST)
        else:
            form = ClaimOrganizationUserAdminForm(request.POST)
        if form.is_valid():
            if registered_user:
                profile = registered_user.get_profile()
                profile.first_name = form.cleaned_data['first_name']
                profile.last_name = form.cleaned_data['last_name']
                profile.id_no = form.cleaned_data['id_no']
                profile.country = form.cleaned_data['country']
                profile.save()

                user = authenticate(invitation_key=invitation.invitation_key)
                OrganizationInvitation.objects.claim_invitation(invitation, registered_user)
            else:
                password = form.cleaned_data['password1']
                user_profile = UserProfile.objects.create_user_profile(
                    email = invitation.admin_email,
                    first_name = form.cleaned_data['first_name'],
                    last_name = form.cleaned_data['last_name'],
                    password = password,
                    id_no = form.cleaned_data['id_no'],
                    country = form.cleaned_data['country'],
                )
                OrganizationInvitation.objects.claim_invitation(invitation, user_profile.user, True)
                user = authenticate(email=invitation.admin_email, password=password)

            # Automatically log user in
            login(request, user)

            messages.success(request, _('You are an administrator of %s successful.') % (invitation.organization_name))
            return redirect('view_organization_front', organization_slug=invitation.organization_slug)

    else:
        if registered_user:
            form = ClaimOrganizationExistUserAdminForm(initial={
                'first_name': registered_user.get_profile().first_name,
                'last_name': registered_user.get_profile().last_name,
            })
        else:
            form = ClaimOrganizationUserAdminForm()

    return render(request, 'manage/organization_invite_claim.html', {
        'invitation':invitation,
        'form':form,
        'first_time':True,
        'registered_user': registered_user,
    })


@login_required
def create_organization(request):
    if not request.user.is_superuser:
        raise Http404

    if request.method == 'POST':
        form = CreateOrganizationForm(request.POST)
        if form.is_valid():
            organization_name = form.cleaned_data['organization_name']
            organization_slug = form.cleaned_data['organization_slug']
            organization_prefix = form.cleaned_data['organization_prefix']
            admin_email = form.cleaned_data['admin_email']
            organization_address = form.cleaned_data['organization_address']
            organization_country = form.cleaned_data['organization_country']
            organization_tel = form.cleaned_data['organization_tel']
            organization_contract_type = form.cleaned_data['organization_contract_type']
            organization_contract_month_remain = form.cleaned_data['organization_contract_month_remain']
            organization_email = form.cleaned_data['organization_email']

            # Send invitation
            try:
                user = User.objects.get(email=admin_email)
            except User.DoesNotExist:
                invitation = OrganizationInvitation.objects.create_invitation(
                    organization_prefix, 
                    organization_name, 
                    organization_slug, 
                    admin_email, 
                    request.user,
                    organization_address,
                    organization_country,
                    organization_tel,
                    organization_contract_type,
                    organization_contract_month_remain,
                    organization_email,
                )
            else:
                invitation = OrganizationInvitation.objects.create_invitation(
                    organization_prefix, 
                    organization_name, 
                    organization_slug, 
                    user.email, 
                    request.user,
                    organization_address,
                    organization_country,
                    organization_tel,
                    organization_contract_type,
                    organization_contract_month_remain,
                    organization_email,
                )
                
            if invitation:
                invitation.send_invitation_email()
                messages.success(request, u'ส่งอีเมลถึงผู้ใช้เพื่อเพิ่มสำนักพิมพ์เรียบร้อย')

            else:
                messages.error(request, u'ไม่สามารถส่งอีเมลถึงผู้ใช้ได้')

            return redirect('manage_organizations')
    
    else:
        form = CreateOrganizationForm()

    return render(request, 'manage/manage_organization_create.html', {'form':form})

@login_required
def edit_organization(request, organization_slug):
    if not request.user.is_superuser:
        raise Http404

    organization = get_object_or_404(Organization, slug=organization_slug)

    if request.method == 'POST':
        form = EditOrganizationForm(organization, request.POST)
        if form.is_valid():
            organization.name = form.cleaned_data['organization_name']
            organization.slug = form.cleaned_data['organization_slug']
            organization.prefix = form.cleaned_data['organization_prefix']

            organization.save()

            return redirect('manage_organizations')
    
    else:
        form = EditOrganizationForm(organization, initial={
            'organization_name': organization.name,
            'organization_slug': organization.slug,
            'organization_prefix': organization.prefix,
        })
    return render(request, 'manage/manage_organization_edit.html', {'organization':organization,'form':form})

