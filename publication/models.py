import uuid

from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.db import models

from private_files import PrivateFileField

def is_downloadable(request, instance):
    return True

def publication_media_dir(instance, filename):
    return '%s%s/%s' % (settings.PUBLICATION_ROOT, instance.publisher.id, filename)

class Publisher(models.Model):
    name = models.CharField(max_length=200)

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='publisher_created_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='publisher_modified_by', null=True)

# class SystemShelf(models.Model):
#     name = models.CharField(max_length=200)

class PublisherShelf(models.Model):
    publisher = models.ForeignKey('Publisher')

    name = models.CharField(max_length=200, default='Default Shelf')
    description = models.CharField(max_length=500, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='publisher_shelf_created_by')

# Publication ############################################################

class UploadingPublication(models.Model):
    publisher = models.ForeignKey('Publisher')

    uid = models.CharField(max_length=200, db_index=True)
    publication_type = models.CharField(max_length=50)

    uploaded_file = models.FileField(upload_to=publication_media_dir, max_length=500)

    file_name = models.CharField(max_length=200)
    file_ext = models.CharField(max_length=10)

    uploaded = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, related_name='uploading_publication_uploaded_by')

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = uuid.uuid4()
        super(UploadingPublication, self).save(*args, **kwargs)

class Publication(models.Model):
    PUBLISH_STATUS_UNPUBLISHED = 1
    PUBLISH_STATUS_READY_TO_PUBLISH = 2
    PUBLISH_STATUS_SCHEDULE_TO_PUBLISH = 3
    PUBLISH_STATUS_PUBLISHED = 4
    
    publisher = models.ForeignKey('Publisher')

    uid = models.CharField(max_length=200, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    publication_type = models.CharField(max_length=50)

    uploaded_file = PrivateFileField(upload_to=publication_media_dir, condition=is_downloadable, max_length=500)
    file_name = models.CharField(max_length=300)
    file_ext = models.CharField(max_length=10)

    publish_status = models.IntegerField(default=PUBLISH_STATUS_UNPUBLISHED)
    publish_schedule = models.DateTimeField(null=True)
    published = models.DateTimeField(null=True, auto_now_add=True)
    published_by = models.ForeignKey(User, null=True, related_name='publication_published_by')

    uploaded = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, related_name='publication_uploaded_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='publication_modified_by', null=True)

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = uuid.uuid4()
        super(Publication, self).save(*args, **kwargs)

class PublicationCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

# Publication - Book ############################################################

class Book(models.Model):
    publication = models.ForeignKey('Publication')
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13)
    categories = models.ManyToManyField('PublicationCategory', related_name='book_categories')

class BookContent(models.Model):
    book = models.ForeignKey('Book')
    title = models.CharField(max_length=255)
    start_page = models.IntegerField()

# Publication - Periodical ############################################################

class Periodical(models.Model):
    publisher = models.ForeignKey('Publisher')

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField('PublicationCategory', related_name='periodical_categories')

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='periodical_created_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='periodical_modified_by', null=True)

class PeriodicalIssue(models.Model):
    publication = models.ForeignKey('Publication')
    periodical = models.ForeignKey('Periodical')

class PeriodicalIssueContent(models.Model):
    issue = models.ForeignKey('PeriodicalIssue')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    start_page = models.IntegerField()
