from django.db import models
from django.contrib.auth.models import User

from accounts.models import UserProfile as BaseUserProfile
from accounts.models import UserOrganization, UserGroup

# from accounts.models import UserProfile as BaseUserProfile

class OrganizationShelf(models.Model):
    organization = models.ForeignKey('accounts.Organization')
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='organization_shelf_created_by')

    def __unicode__(self):
        return '%s:%s' % (self.organization.name, self.name)

class OrganizationTag(models.Model):
    organization = models.ForeignKey('accounts.Organization')
    tag_name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='organization_tag_created_by')

class Document(models.Model):
    publication = models.OneToOneField('publication.Publication')
    shelves = models.ManyToManyField(OrganizationShelf, through='DocumentShelf')
    tags = models.ManyToManyField(OrganizationTag, through='DocumentTag')

class DocumentShelf(models.Model):
    document = models.ForeignKey(Document)
    shelf = models.ForeignKey(OrganizationShelf)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='document_shelf_created_by')

class DocumentTag(models.Model):
    document = models.ForeignKey(Document)
    tag = models.ForeignKey(OrganizationTag)

class UserProfile(BaseUserProfile):
    
    def get_viewable_shelves(self, organization):
        shelves = set()
        
        for group in UserGroup.objects.filter(user=self.user):
            for shelf_permission in ShelfPermission.objects.filter(group=group):
                if shelf_permission.access_level >= SHELF_ACCESS['VIEW_ACCESS']:
                    shelves.append(shelf_permission.shelf)
        
        return shelves
    
    def get_shelf_access(self, shelf):
        role = UserOrganization.objects.get(user=self.user, organization=shelf.organization).role
        try:
            return RoleShelfPermission.objects.get(role=role, shelf=shelf).access_level
        except:
            return SHELF_ACCESS['NO_ACCESS']

# Shelf Permissions

SHELF_ACCESS = {'NO_ACCESS':0, 'VIEW_ACCESS':1, 'PUBLISH_ACCESS':2}

class ShelfPermission(models.Model):
    group = models.ForeignKey('accounts.OrganizationGroup')
    shelf = models.ForeignKey(OrganizationShelf)
    access_level = models.IntegerField(default=SHELF_ACCESS['NO_ACCESS']) # 0 = NO ACCESS, 1 = VIEW ONLY, 2 = PUBLISH/EDIT
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='shelf_permission_created_by')
