from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class Magazine(models.Model):
    organization = models.ForeignKey('accounts.Organization')

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    categories = models.ManyToManyField(Category, related_name='magazine_categories', null=True, blank=True)

    logo = models.ImageField(upload_to=settings.MAGAZINE_LOGO_ROOT, max_length=500, null=True)

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='magazine_created_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='magazine_modified_by', null=True, blank=True)

    def __unicode__(self):
        return self.title

class MagazineIssue(models.Model):
    publication = models.OneToOneField('publication.Publication')
    magazine = models.ForeignKey(Magazine)

class Book(models.Model):
    organization = models.OneToOneField('accounts.Organization')
    author = models.CharField(max_length=300)
    categories = models.ManyToManyField(Category, related_name='book_categories', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
