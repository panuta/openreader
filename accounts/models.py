# -*- encoding: utf-8 -*-

import random
import re

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User, Permission
from django.db import models
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor

from common.permissions import can

"""
User Type
1. Reader [web_access=False]
   This user can only use an app on a device. Cannot login to website.

2. Organization/Admin
   This user can do
      - Organization management (Details, Users, Billing)
      - Publish permission
      - Publication management (Upload/Edit/Delete)
      - View all organization's publication

3. Organization/Staff
   This user can do
      - Publication management (Upload/Edit/Delete)
      - View all organization's publication

4. Organization/User
   This user can do
      - View all organization's publication
"""

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class Role(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=200) # first_name and last_name in contrib.auth.User is too short
    last_name = models.CharField(max_length=200)
    web_access = models.BooleanField()
    is_first_time = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def can(self, action, object):
        return can(self.user, action, object)

    def get_fullname(self):
        if not self.first_name or not self.last_name:
            if not self.user.first_name or not self.user.last_name:
                return self.user.email
            return '%s %s' % (self.user.first_name, self.user.last_name)
        return '%s %s' % (self.first_name, self.last_name)

# Organization

class Organization(models.Model):
    name = models.CharField(max_length=200)
    prefix = models.CharField(max_length=200, default='บริษัท')
    status = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='organization_created_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='organization_modified_by', null=True, blank=True)

    def __unicode__(self):
        return self.name

    def can_view(self, user):
        return UserOrganization.objects.filter(user=user, organization=self).exists()

    def can_edit(self, user):
        try:
            user_organization = UserOrganization.objects.get(organization=self, user=user)
            return user_organization.role.code in ('organization_admin', 'organization_staff')
        except UserOrganization.DoesNotExist:
            return False
    
    def can_manage(self, user):
        try:
            user_organization = UserOrganization.objects.get(organization=self, user=user)
            return user_organization.role.code in ('organization_admin', )
        except UserOrganization.DoesNotExist:
            return False

class UserOrganization(models.Model):
    user = models.ForeignKey(User)
    organization = models.ForeignKey(Organization)
    role = models.ForeignKey(Role)
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s:%s' % (self.user.get_profile().get_fullname(), self.organization.name)

# User / Invitation

class UserInvitationManager(models.Manager):

    def create_invitation(self, user_email, organization, role, created_by):
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        if isinstance(user_email, unicode):
            user_email = user_email.encode('utf-8')
        invitation_key = sha_constructor(salt+user_email).hexdigest()

        return self.create(user_email=user_email, organization=organization, role=role, invitation_key=invitation_key, created_by=created_by)
    
    def validate_invitation(self, invitation_key):
        if SHA1_RE.search(invitation_key):
            try:
                return self.get(invitation_key=invitation_key)
            except UserOrganizationInvitation.DoesNotExist:
                return None
        else:
            return None
    
    def claim_invitation(self, invitation, user, is_default=False):
        user_organization = UserOrganization.objects.create(user=user, organization=invitation.organization, role=invitation.role, is_default=is_default)
        invitation.delete()
        return user_organization

class UserOrganizationInvitation(models.Model):
    user_email = models.CharField(max_length=200, null=True, blank=True)
    organization = models.ForeignKey(Organization)
    role = models.ForeignKey(Role)
    invitation_key = models.CharField(max_length=40, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='user_invitation_created_by')

    def __unicode__(self):
        return '%s:%s' % (self.user_email, self.organization.name)

    objects = UserInvitationManager()

    def send_invitation_email(self, is_created_organization=False):
        try:
            send_mail('%s want to invite you to join their team' % self.organization.name, render_to_string('publisher/email_templates/user_organization_invitation.html', {'invitation':self }), settings.EMAIL_FOR_USER_PUBLISHER_INVITATION, [self.user_email], fail_silently=False)
            return True
        except:
            return False


class UserDevice(models.Model):
    user = models.ForeignKey(User)
    device_id = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s:%s' % (self.user.get_profile().get_fullname(), self.device_id)

class UserAccessToken(models.Model):
    user = models.ForeignKey(User)
    token = models.CharField(max_length=300)
    expired = models.DateField()
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s:%s' % (self.user.get_profile().get_fullname(), self.token)
