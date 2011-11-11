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

class PublisherModule(models.Model):
    publisher = models.ForeignKey('Publisher')
    module_name = models.CharField(max_length=100)
    module_type = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)

    def get_module_object(self):
        return __import__('publication.%s' % self.module_name, fromlist=['publication'])

class PublisherShelf(models.Model):
    publisher = models.ForeignKey('Publisher')

    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='publisher_shelf_created_by')

# Publication ############################################################

class UploadingPublication(models.Model):
    publisher = models.ForeignKey('Publisher')

    uid = models.CharField(max_length=200, db_index=True)
    publication_type = models.CharField(max_length=50)
    parent_id = models.IntegerField(null=True) # Can be used for Magazine ID, etc.

    uploaded_file = models.FileField(upload_to=publication_media_dir, max_length=500)

    original_file_name = models.CharField(max_length=200)
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
    publication_type = models.CharField(max_length=50) # Also module_code

    uploaded_file = PrivateFileField(upload_to=publication_media_dir, condition=is_downloadable, max_length=500, null=True)
    original_file_name = models.CharField(max_length=300)
    file_ext = models.CharField(max_length=10)

    publish_status = models.IntegerField(default=PUBLISH_STATUS_UNPUBLISHED)
    publish_schedule = models.DateTimeField(null=True)
    published = models.DateTimeField(null=True)
    published_by = models.ForeignKey(User, null=True, related_name='publication_published_by')

    uploaded = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, related_name='publication_uploaded_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='publication_modified_by', null=True)

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = uuid.uuid4()
        super(Publication, self).save(*args, **kwargs)
    
    def get_publication_title(self):
        from publication import get_publication_module
        return get_publication_module(self.publication_type).get_publication_title(self)

class PublicationCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


