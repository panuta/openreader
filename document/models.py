from django.db import models
from django.contrib.auth.models import User

from accounts.models import UserProfile as BaseUserProfile
from accounts.models import UserOrganization, UserGroup

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

    def check_permission(self, action, parameters):
        print parameters
        try:
            if action == 'view_shelf':
                return get_shelf_access(parameters['shelf']) >= SHELF_ACCESS['VIEW_ACCESS']
            
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
                shelf_access = get_shelf_access(shelf)
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

# Shelf Permissions

SHELF_ACCESS = {'NO_ACCESS':0, 'VIEW_ACCESS':1, 'PUBLISH_ACCESS':2}

class ShelfPermission(models.Model):
    group = models.ForeignKey('accounts.OrganizationGroup')
    shelf = models.ForeignKey(OrganizationShelf)
    access_level = models.IntegerField(default=SHELF_ACCESS['NO_ACCESS']) # 0 = NO ACCESS, 1 = VIEW ONLY, 2 = PUBLISH/EDIT
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='shelf_permission_created_by')
