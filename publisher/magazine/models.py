from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from publisher.models import Publisher, Publication, PublicationCategory

class Magazine(models.Model):
    publisher = models.ForeignKey(Publisher)

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    categories = models.ManyToManyField(PublicationCategory, related_name='magazine_categories', null=True, blank=True)

    logo = models.ImageField(upload_to=settings.MAGAZINE_LOGO_ROOT, max_length=500, null=True)

    cancel_with_issue = models.ForeignKey('MagazineIssue', related_name='cancel_with', null=True)

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='magazine_created_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='magazine_modified_by', null=True, blank=True)

    def __unicode__(self):
        return self.title

class MagazineIssue(models.Model):
    publication = models.OneToOneField(Publication)
    magazine = models.ForeignKey(Magazine)

class MagazineIssueContent(models.Model):
    issue = models.ForeignKey(MagazineIssue)
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=300, null=True, blank=True)
    start_page = models.IntegerField()