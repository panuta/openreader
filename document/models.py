# -*- encoding: utf-8 -*-
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
    return '%s%s/%s' % (settings.PUBLICATION_ROOT, instance.organization.id, filename)

class Publication(models.Model):
    organization = models.ForeignKey('accounts.Organization')

    uid = models.CharField(max_length=200, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    
    uploaded_file = PrivateFileField(upload_to=publication_media_dir, condition=is_downloadable, max_length=500, null=True)
    #uploaded_file = models.FileField(upload_to='/web/sites/openreader/files/', max_length=500, null=True)
    original_file_name = models.CharField(max_length=300)
    file_ext = models.CharField(max_length=10)
    has_thumbnail = models.BooleanField(default=False)

    shelves = models.ManyToManyField('OrganizationShelf', through='PublicationShelf')
    tags = models.ManyToManyField('OrganizationTag', through='PublicationTag')

    uploaded = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, related_name='publication_uploaded_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='publication_modified_by', null=True, blank=True)

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
    
    def get_download_url(self):
        pass

# SHELF
############################################################

class OrganizationShelf(models.Model):
    organization = models.ForeignKey('accounts.Organization')
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='organization_shelf_created_by')

    def __unicode__(self):
        return self.name

class PublicationShelf(models.Model):
    publication = models.ForeignKey(Publication)
    shelf = models.ForeignKey(OrganizationShelf)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='publication_shelf_created_by')

# TAG
############################################################

class OrganizationTag(models.Model):
    organization = models.ForeignKey('accounts.Organization')
    tag_name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='organization_tag_created_by')

class PublicationTag(models.Model):
    publication = models.ForeignKey(Publication)
    tag = models.ForeignKey(OrganizationTag)

# USER PROFILE
############################################################

class UserProfile(BaseUserProfile):

    def check_permission(self, action, parameters):
        try:
            if action == 'view_shelf':
                return self.get_shelf_access(parameters['shelf']) >= SHELF_ACCESS['VIEW_ACCESS']
            
            if action == 'upload_shelf':
                return self.get_shelf_access(parameters['shelf']) == SHELF_ACCESS['PUBLISH_ACCESS']
            
        except:
            pass
        
        return BaseUserProfile.check_permission(self, action, parameters)
    
    def get_viewable_shelves(self, organization):
        user_organization = UserOrganization.objects.get(user=self.user, organization=organization)

        if user_organization.is_admin:
            return OrganizationShelf.objects.filter(organization=organization).order_by('name')
        else:
            shelves = []
            for shelf in OrganizationShelf.objects.filter(organization=organization).order_by('name'):
                shelf_access = self.get_shelf_access(shelf)
                if shelf_access >= SHELF_ACCESS['VIEW_ACCESS']:
                    shelves.append(shelf)
        
            return shelves
    
    def get_shelf_access(self, shelf):
        level = SHELF_ACCESS['NO_ACCESS']

        user_organization = UserOrganization.objects.get(user=self.user, organization=shelf.organization)
        for group in UserGroup.objects.filter(user_organization=user_organization):

            try:
                access_level = ShelfPermission.objects.get(group=group, shelf=shelf).access_level
            except:
                access_level = SHELF_ACCESS['NO_ACCESS']

            if level < access_level:
                level = access_level
        
        return level

SHELF_ACCESS = {'NO_ACCESS':0, 'VIEW_ACCESS':1, 'PUBLISH_ACCESS':2}

class ShelfPermission(models.Model):
    group = models.ForeignKey('accounts.OrganizationGroup')
    shelf = models.ForeignKey(OrganizationShelf)
    access_level = models.IntegerField(default=SHELF_ACCESS['NO_ACCESS']) # 0 = NO ACCESS, 1 = VIEW ONLY, 2 = PUBLISH/EDIT
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='shelf_permission_created_by')
