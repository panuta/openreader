# -*- encoding: utf-8 -*-

import random
import re

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor

from common.permissions import can

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    email = models.CharField(max_length=254) # use this field as username to login
    first_name = models.CharField(max_length=100) # first_name and last_name in contrib.auth.User is too short
    last_name = models.CharField(max_length=100)
    web_access = models.BooleanField(default=True)
    is_first_time = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_fullname(self):
        if not self.first_name or not self.last_name:
            if not self.user.first_name or not self.user.last_name:
                return self.user.email
            return '%s %s' % (self.user.first_name, self.user.last_name)
        return '%s %s' % (self.first_name, self.last_name)
    
    def get_instance_from_email(email):
        app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
        model = models.get_model(app_label, model_name)

        try:
            return model._default_manager.get(email=email)
        except:
            return None

# Admin Permissions
class OrganizationAdminPermission(models.Model):
    name = models.CharField(max_length=200)
    code_name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

# Organization

class Organization(models.Model):
    name = models.CharField(max_length=200)
    prefix = models.CharField(max_length=200, default='บริษัท')
    slug = models.CharField(max_length=200, unique=True, db_index=True)
    status = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='organization_created_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='organization_modified_by', null=True, blank=True)

    def __unicode__(self):
        return self.name

class OrganizationGroup(models.Model):
    organization = models.ForeignKey(Organization)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)

    def __unicode__(self):
        return self.name

class UserOrganization(models.Model):
    user = models.ForeignKey(User)
    organization = models.ForeignKey(Organization)
    is_admin = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(OrganizationGroup, through='UserGroup')
    admin_permissions = models.ManyToManyField(OrganizationAdminPermission)

    def __unicode__(self):
        return '%s:%s' % (self.user.get_profile().get_fullname(), self.organization.name)

class UserGroup(models.Model):
    user_organization = models.ForeignKey(UserOrganization)
    group = models.ForeignKey(OrganizationGroup)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s:%s' % (self.user.get_profile().get_fullname(), self.group.name)

# User Invitation

class UserInvitationManager(models.Manager):

    def create_invitation(self, email, organization, admin_permissions, groups, created_by):
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        if isinstance(email, unicode):
            email = email.encode('utf-8')
        invitation_key = sha_constructor(salt + email).hexdigest()

        invitation = self.create(email=email, organization=organization, invitation_key=invitation_key, created_by=created_by)
        invitation.admin_permissions = admin_permissions

        for group in groups:
            UserOrganizationInvitationUserGroup.objects.create(invitation=invitation, group=group)

        return invitation
    
    def validate_invitation(self, invitation_key):
        if SHA1_RE.search(invitation_key):
            try:
                return self.get(invitation_key=invitation_key)
            except UserOrganizationInvitation.DoesNotExist:
                return None
        else:
            return None
    
    def claim_invitation(self, invitation, user, is_default=False):
        user_organization = UserOrganization.objects.create(user=user, organization=invitation.organization, is_default=is_default)
        user_organization.admin_permissions = invitation.admin_permissions.all()

        for invitation_group in UserOrganizationInvitationUserGroup.objects.filter(invitation=invitation):
            UserGroup.objects.create(user_organization=user_organization, group=invitation_group.group)
        
        UserOrganizationInvitationUserGroup.objects.filter(invitation=invitation).delete()
        invitation.delete()

        return user_organization

class UserOrganizationInvitation(models.Model):
    email = models.CharField(max_length=200, null=True, blank=True)
    organization = models.ForeignKey(Organization)
    invitation_key = models.CharField(max_length=40, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='user_invitation_created_by')

    groups = models.ManyToManyField(OrganizationGroup, through='UserOrganizationInvitationUserGroup')
    admin_permissions = models.ManyToManyField(OrganizationAdminPermission)

    def __unicode__(self):
        return '%s:%s' % (self.email, self.organization.name)

    objects = UserInvitationManager()

    def send_invitation_email(self, is_created_organization=False):
        try:
            send_mail('%s want to invite you to join their team' % self.organization.name, render_to_string('accounts/manage/emails/user_organization_invitation.html', {'invitation':self }), settings.EMAIL_FOR_USER_PUBLISHER_INVITATION, [self.email], fail_silently=False)
            return True
        except:
            return False

class UserOrganizationInvitationUserGroup(models.Model):
    invitation = models.ForeignKey(UserOrganizationInvitation)
    group = models.ForeignKey(OrganizationGroup)
