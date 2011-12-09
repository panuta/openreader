from django.db import models

from django.contrib.auth.models import User

class OrganizationShelf(models.Model):
    organization = models.ForeignKey('accounts.Organization')
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='organization_shelf_created_by')

    def __unicode__(self):
        return '%s:%s' % (self.organization.name, self.name)

class UserShelfPermission(models.Model):
    user = models.ForeignKey(User)
    shelf = models.ForeignKey(OrganizationShelf)
    can_view = models.BooleanField(default=False)
    can_publish = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='user_shelf_permission_created_by')

class Document(models.Model):
    publication = models.ForeignKey('publication.Publication')
    shelves = models.ManyToManyField(OrganizationShelf, through='DocumentShelf')

class DocumentShelf(models.Model):
    document = models.ForeignKey(Document)
    shelf = models.ForeignKey(OrganizationShelf)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='document_shelf_created_by')