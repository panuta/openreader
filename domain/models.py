# -*- encoding: utf-8 -*-

import re
import shortuuid
import uuid

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string
from django.utils.crypto import salted_hmac

from private_files import PrivateFileField

from common.thumbnails import get_thumbnail_url

SHA1_RE = re.compile('^[a-f0-9]{40}$')

# USER ACCOUNT
##############################################################################################################

class UserProfileManager(models.Manager):

    def create_user_profile(self, email, first_name, last_name, password, web_access=True, update_if_exists=False):
        try:
            user = User.objects.get(email=email)
            user_profile = user.get_profile()

            if update_if_exists:
                user.email = email
                user.set_password(password)
                user.save()

                user_profile.first_name = first_name
                user_profile.last_name = last_name
                user_profile.save()

        except User.DoesNotExist:
            user = User.objects.create_user(shortuuid.uuid(), email, password)
            user_profile = UserProfile.objects.create(user=user, first_name=first_name, last_name=last_name, web_access=web_access)

        return user_profile


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=100) # first_name and last_name in contrib.auth.User is too short
    last_name = models.CharField(max_length=100)
    web_access = models.BooleanField(default=True)
    is_first_time = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

    objects = UserProfileManager()

    def get_fullname(self):
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
    created_by = models.ForeignKey(User, related_name='created_organizations')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='modified_organizations', null=True, blank=True)

    def __unicode__(self):
        return self.name

    def _get_organization_shelf_count(self):
        return OrganizationShelf.objects.filter(organization=self).count()

    shelf_count = property(_get_organization_shelf_count)

class OrganizationGroup(models.Model):
    organization = models.ForeignKey(Organization)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)

    def __unicode__(self):
        return self.name

    def get_user_count(self):
        return UserGroup.objects.filter(group=self).count()

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
        key_salt = 'domain.models.UserInvitationManager'
        email = email.encode('utf-8')
        invitation_key = salted_hmac(key_salt, email).hexdigest()

        invitation = self.create(email=email, organization=organization, invitation_key=invitation_key, created_by=created_by)
        invitation.admin_permissions = admin_permissions
        invitation.groups = groups

        return invitation

    def claim_invitation(self, invitation, user, is_default=False):
        try:
            UserOrganization.objects.get(user=user)
        except UserOrganization.DoesNotExist:
            user_organization = UserOrganization.objects.create(user=user, organization=invitation.organization, is_default=is_default)
            user_organization.admin_permissions = invitation.admin_permissions.all()

            for group in invitation.groups.all():
                UserGroup.objects.create(user_organization=user_organization, group=group)

        invitation.delete()
        return user_organization

class UserOrganizationInvitation(models.Model):
    email = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization)
    invitation_key = models.CharField(max_length=40, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_invitations')

    groups = models.ManyToManyField(OrganizationGroup)
    admin_permissions = models.ManyToManyField(OrganizationAdminPermission)

    def __unicode__(self):
        return '%s:%s' % (self.email, self.organization.name)

    objects = UserInvitationManager()

    def send_invitation_email(self):
        try:
            send_mail('You were invited to join %s account in %s' % (self.organization.name, settings.WEBSITE_NAME), render_to_string('organization/emails/user_organization_invitation.html', {'invitation':self }), settings.EMAIL_ADDRESS_NO_REPLY, [self.email], fail_silently=False)
            return True
        except:
            return False

"""
class UserOrganizationInvitationUserGroup(models.Model):
    invitation = models.ForeignKey(UserOrganizationInvitation)
    group = models.ForeignKey(OrganizationGroup)
"""
# DOCUMENT
##############################################################################################################

def is_downloadable(request, instance):
    return True

def publication_media_dir(instance, filename):
    return '%s/%s/%s' % (settings.PUBLICATION_ROOT, instance.organization.id, filename)

class Publication(models.Model):
    organization = models.ForeignKey(Organization)

    uid = models.CharField(max_length=200, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)

    uploaded_file = PrivateFileField(upload_to=publication_media_dir, condition=is_downloadable, max_length=500)
    original_file_name = models.CharField(max_length=300)
    file_ext = models.CharField(max_length=10)

    is_processing = models.BooleanField(default=True)
    has_thumbnail = models.BooleanField(default=False)

    shelves = models.ManyToManyField('OrganizationShelf', through='PublicationShelf')
    tags = models.ManyToManyField('OrganizationTag', through='PublicationTag')

    uploaded = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, related_name='uploaded_publications')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='modified_publications', null=True, blank=True)
    replaced = models.DateTimeField(null=True, blank=True)
    replaced_by = models.ForeignKey(User, related_name='replaced_publications', null=True, blank=True)

    def __unicode__(self):
        return '%s' % (self.title)

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = uuid.uuid4()
        super(Publication, self).save(*args, **kwargs)

    def get_large_thumbnail(self):
        return get_thumbnail_url(self, 'large')

    def get_small_thumbnail(self):
        return get_thumbnail_url(self, 'small')

    def get_parent_folder(self):
        return '/%s' % self.organization.id

    def get_rel_path(self): # return -> /[org id]
        return '/%d' % (settings.PUBLICATION_PREFIX, self.organization.id)

    def get_download_rel_path(self): # return -> /[org id]/[uid].[file-ext]
        if self.file_ext:
            return '%s/%s.%s' % (self.get_parent_folder(), self.uid, self.file_ext)
        else:
            return '%s/%s' % (self.get_parent_folder(), self.uid)

"""
class PublicationRevision(models.Model):
    uid = models.CharField(max_length=200, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)

    uploaded_file = PrivateFileField(upload_to=publication_media_dir, condition=is_downloadable, max_length=500, null=True)
    original_file_name = models.CharField(max_length=300)
    file_ext = models.CharField(max_length=10)
    has_thumbnail = models.BooleanField(default=False)

    shelves = models.ManyToManyField('OrganizationShelf', through='PublicationShelf')
    tags = models.ManyToManyField('OrganizationTag', through='PublicationTag')

    modified = models.DateTimeField()
    modified_by = models.ForeignKey(User, related_name='publication_revision_modified_by')
"""

# SHELF

SHELF_ACCESS = {'NO_ACCESS':0, 'VIEW_ACCESS':1, 'PUBLISH_ACCESS':2}

class OrganizationShelf(models.Model):
    organization = models.ForeignKey(Organization)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    icon = models.CharField(max_length=100)
    auto_sync = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_organization_shelves')

    def __unicode__(self):
        return self.name

    def _get_publication_count(self):
        return PublicationShelf.objects.filter(shelf=self).count()

    num_of_publications = property(_get_publication_count)

    def _get_latest_publication(self):
        publications = Publication.objects.filter(shelves__in=[self]).order_by('-uploaded')
        if publications:
            return publications[0]

        return None

    latest_publication = property(_get_latest_publication)


class PublicationShelf(models.Model):
    publication = models.ForeignKey(Publication)
    shelf = models.ForeignKey(OrganizationShelf)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_publication_shelves')

class OrganizationShelfPermission(models.Model):
    shelf = models.OneToOneField(OrganizationShelf)
    access_level = models.IntegerField(default=SHELF_ACCESS['NO_ACCESS'])
    created = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='created_organization_shelf_permissions')

class GroupShelfPermission(models.Model):
    group = models.ForeignKey(OrganizationGroup)
    shelf = models.ForeignKey(OrganizationShelf)
    access_level = models.IntegerField(default=SHELF_ACCESS['NO_ACCESS'])
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_group_shelf_permissions')

class UserShelfPermission(models.Model):
    user = models.ForeignKey(User)
    shelf = models.ForeignKey(OrganizationShelf)
    access_level = models.IntegerField(default=SHELF_ACCESS['NO_ACCESS'])
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_user_shelf_permissions')

# TAG

class OrganizationTag(models.Model):
    organization = models.ForeignKey(Organization)
    tag_name = models.CharField(max_length=200)

class PublicationTag(models.Model):
    publication = models.ForeignKey(Publication)
    tag = models.ForeignKey(OrganizationTag)

# ORGANIZATION SERVER

class OrganizationDownloadServer(models.Model):
    organization = models.ForeignKey(Organization)
    priority = models.IntegerField(default=0) # Higher value has higher priority
    server_type = models.CharField(max_length=200) # nginx, s3, intranet, xsendfile
    server_address = models.CharField(max_length=300)
    parameters = models.CharField(max_length=2000)

class OrganizationUploadServer(models.Model):
    organization = models.ForeignKey(Organization)
    server_type = models.CharField(max_length=200) # sftp, s3
    server_address = models.CharField(max_length=300)
    parameters = models.CharField(max_length=2000)