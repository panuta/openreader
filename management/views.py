# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from domain.models import User, Organization, UserOrganization, UserOrganizationInvitation, OrganizationAdminPermission, OrganizationGroup

from forms import *

def manage_front(request):
    return redirect('manage_organizations')

@login_required
def manage_organizations(request):
    if not request.user.is_superuser:
        raise Http404
    
    organizations = Organization.objects.all().order_by('name')
    return render(request, 'manage/manage_organizations.html', {'organizations':organizations})

@login_required
def manage_organization(request, organization_slug):
    if not request.user.is_superuser:
        raise Http404

    organization = get_object_or_404(Organization, slug=organization_slug)
    return render(request, 'manage/manage_organization.html', {'organization':organization})

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

            organization = Organization.objects.create(name=organization_name, slug=organization_slug, prefix=organization_prefix, created_by=request.user)

            # Send invitation
            
            try:
                user = User.objects.get(email=admin_email)
            except User.DoesNotExist:
                invitation = UserOrganizationInvitation.objects.create_invitation(admin_email, organization, [], request.user)
            else:
                invitation = UserOrganizationInvitation.objects.create_invitation(user.email, organization, [], request.user)                
                
            if invitation:
                invitation.send_invitation_email()
                messages.success(request, u'เพิ่มสำนักพิมพ์ และส่งอีเมลถึงผู้ใช้เรียบร้อย')

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
        form = EditOrganizationForm(request.POST)
        if form.is_valid():
            organization.name = form.cleaned_data['organization_name']
            organization.slug = form.cleaned_data['organization_slug']
            organization.prefix = form.cleaned_data['organization_prefix']

            organization.save()

            return redirect('manage_organizations')
    
    else:
        form = EditOrganizationForm(initial={
            'organization_name': organization.name,
            'organization_slug': organization.slug,
            'organization_prefix': organization.prefix,
        })
    return render(request, 'manage/manage_organization_edit.html', {'organization':organization,'form':form})

