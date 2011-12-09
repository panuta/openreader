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
    return redirect('manage_publishers')

@login_required
def manage_publishers(request):
    if not request.user.is_superuser: raise Http404
    
    publishers = Publisher.objects.all().order_by('name')
    
    return render(request, 'manage/manage_publishers.html', {'publishers':publishers})

@login_required
def manage_publisher(request, publisher_id):
    if not request.user.is_superuser: raise Http404

    publisher = get_object_or_404(Publisher, id=publisher_id)
    
    return render(request, 'manage/manage_publisher.html', {'publisher':publisher})

@login_required
def create_publisher(request):
    if not request.user.is_superuser: raise Http404

    if request.method == 'POST':
        form = CreatePublisherForm(request.POST)
        if form.is_valid():
            publisher_name = form.cleaned_data['publisher_name']
            modules = form.cleaned_data['modules']
            admin_email = form.cleaned_data['admin_email']

            publisher = Publisher.objects.create(name=publisher_name, created_by=request.user)

            for module in modules:
                PublisherModule.objects.create(publisher=publisher, module=module)

            # Send invitation
            publisher_admin_role = Role.objects.get(code='publisher_admin')

            try:
                user = User.objects.get(email=admin_email)
            except User.DoesNotExist:
                invitation = UserPublisherInvitation.objects.create_invitation(admin_email, publisher, publisher_admin_role, request.user)
            else:
                invitation = UserPublisherInvitation.objects.create_invitation(user.email, publisher, publisher_admin_role, request.user)                
            
            if invitation:
                invitation.send_invitation_email(is_created_publisher=True)

                messages.success(request, u'เพิ่มสำนักพิมพ์ และส่งอีเมลถึงผู้ใช้เรียบร้อย')

            else:
                messages.error(request, u'ไม่สามารถส่งอีเมลถึงผู้ใช้ได้')

            return redirect('manage_publishers')
    
    else:
        form = CreatePublisherForm()

    return render(request, 'manage/manage_publisher_create.html', {'form':form})

