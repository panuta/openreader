# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Role, Organization, UserOrganization, UserOrganizationInvitation

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
def manage_organization(request, organization_id):
    if not request.user.is_superuser:
        raise Http404

    organization = get_object_or_404(Organization, id=organization_id)
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
            organization_admin_role = Role.objects.get(code='organization_admin')

            try:
                user = User.objects.get(email=admin_email)
            except User.DoesNotExist:
                invitation = UserOrganizationInvitation.objects.create_invitation(admin_email, organization, organization_admin_role, request.user)
            else:
                invitation = UserOrganizationInvitation.objects.create_invitation(user.email, organization, organization_admin_role, request.user)                
            
            if invitation:
                invitation.send_invitation_email(is_created_organization=True)

                messages.success(request, u'เพิ่มสำนักพิมพ์ และส่งอีเมลถึงผู้ใช้เรียบร้อย')

            else:
                messages.error(request, u'ไม่สามารถส่งอีเมลถึงผู้ใช้ได้')

            return redirect('manage_organizations')
    
    else:
        form = CreateOrganizationForm()

    return render(request, 'manage/manage_organization_create.html', {'form':form})

