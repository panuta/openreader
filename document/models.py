# -*- encoding: utf-8 -*-
import os
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from private_files import PrivateFileField

from common.thumbnails import get_thumbnail_url

from accounts.models import UserProfile as BaseUserProfile
from accounts.models import UserOrganization, UserGroup

# PUBLICATION
############################################################

def is_downloadable(request, instance):
    return True

def publication_media_dir(instance, filename):
    return '%s/%s/%s' % (settings.PUBLICATION_ROOT, instance.organization.id, filename)

class Publication(models.Model):
    organization = models.ForeignKey('accounts.Organization')

    uid = models.CharField(max_length=200, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    
    uploaded_file = PrivateFileField(upload_to=publication_media_dir, condition=is_downloadable, max_length=500, null=True)
    #uploaded_file = models.FileField(upload_to='/web/sites/openreader/files/', max_length=500, null=True)
    original_file_name = models.CharField(max_length=300)
    file_ext = models.CharField(max_length=10)

    is_processing = models.BooleanField(default=True)
    has_thumbnail = models.BooleanField(default=False)

    shelves = models.ManyToManyField('OrganizationShelf', through='PublicationShelf')
    tags = models.ManyToManyField('OrganizationTag', through='PublicationTag')

    uploaded = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, related_name='publication_uploaded_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='publication_modified_by', null=True)
    replaced = models.DateTimeField(null=True)
    replaced_by = models.ForeignKey(User, related_name='publication_replaced_by', null=True)

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
        return '%s/%d' % (settings.PUBLICATION_PREFIX, self.organization.id)
    
    def get_download_rel_path(self): # return -> /[org id]/[uid].[file-ext]
        return self.uploaded_file.path.replace(settings.PUBLICATION_ROOT, '')

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
############################################################

SHELF_ACCESS = {'NO_ACCESS':0, 'VIEW_ACCESS':1, 'PUBLISH_ACCESS':2}

class OrganizationShelf(models.Model):
    organization = models.ForeignKey('accounts.Organization')
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    icon = models.CharField(max_length=100)
    auto_sync = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='organization_shelf_created_by')

    def __unicode__(self):
        return self.name

class PublicationShelf(models.Model):
    publication = models.ForeignKey(Publication)
    shelf = models.ForeignKey(OrganizationShelf)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='publication_shelf_created_by')

class OrganizationShelfPermission(models.Model):
    shelf = models.OneToOneField(OrganizationShelf)
    access_level = models.IntegerField(default=SHELF_ACCESS['NO_ACCESS'])
    created = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='organization_shelf_permission_created_by')

class GroupShelfPermission(models.Model):
    group = models.ForeignKey('accounts.OrganizationGroup')
    shelf = models.ForeignKey(OrganizationShelf)
    access_level = models.IntegerField(default=SHELF_ACCESS['NO_ACCESS'])
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='group_shelf_permission_created_by')

class UserShelfPermission(models.Model):
    user = models.ForeignKey(User)
    shelf = models.ForeignKey(OrganizationShelf)
    access_level = models.IntegerField(default=SHELF_ACCESS['NO_ACCESS'])
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='user_shelf_permission_created_by')

# TAG
############################################################

class OrganizationTag(models.Model):
    organization = models.ForeignKey('accounts.Organization')
    tag_name = models.CharField(max_length=200)

class PublicationTag(models.Model):
    publication = models.ForeignKey(Publication)
    tag = models.ForeignKey(OrganizationTag)

# DOWNLOAD SERVER
############################################################

class OrganizationDownloadServer(models.Model):
    organization = models.ForeignKey('accounts.Organization')
    priority = models.IntegerField(default=0) # Higher value has higher priority
    server_type = models.CharField(max_length=200)
    server_address = models.CharField(max_length=300)
    parameters = models.CharField(max_length=2000)
    # prefix = models.CharField(max_length=300, blank=True, null=True) # e.g. '/openreader' (remove trailing slash)
    # key = models.CharField(max_length=300, blank=True, null=True)

