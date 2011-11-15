import uuid

from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.db import models
from django.db.models import Q

from private_files import PrivateFileField

from accounts.models import UserPublisher

def is_downloadable(request, instance):
    return True

def publication_media_dir(instance, filename):
    return '%s%s/%s' % (settings.PUBLICATION_ROOT, instance.publisher.id, filename)

class Publisher(models.Model):
    name = models.CharField(max_length=200)

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='publisher_created_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='publisher_modified_by', null=True, blank=True)

    def __unicode__(self):
        return self.name

    def can_view(self, user):
        return UserPublisher.objects.filter(user=user, publisher=self).exists()

    def can_publish(self, user):
        #return True
        return user.groups.filter(Q(name='publisher_admin') | Q(name='publisher_staff')).exists()
    
    def can_upload(self, user):
        #return True
        return self.can_publish(user)
    
    def can_manage(self, user):
        return user.groups.filter(name='publisher_admin').exists()

# class SystemShelf(models.Model):
#     name = models.CharField(max_length=200)

class Module(models.Model):
    module_name = models.CharField(max_length=100)
    module_type = models.CharField(max_length=50)

    def __unicode__(self):
        return '%s [%s]' % (self.module_name, self.module_type)
    
    def get_module_object(self, sub_module=''):
        if sub_module:
            sub_module = '.' + sub_module
        
        try:
            return __import__('publication.%s%s' % (self.module_name, sub_module), fromlist=['publication'])
        except:
            return None

class PublisherModule(models.Model):
    publisher = models.ForeignKey('Publisher')
    module = models.ForeignKey('Module')
    created = models.DateTimeField(auto_now_add=True)

class PublisherShelf(models.Model):
    publisher = models.ForeignKey('Publisher')

    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='publisher_shelf_created_by')

    def __unicode__(self):
        return self.name

# Publication ############################################################

class UploadingPublication(models.Model):
    publisher = models.ForeignKey('Publisher')

    uid = models.CharField(max_length=200, db_index=True)
    publication_type = models.CharField(max_length=50)
    parent_id = models.IntegerField(null=True, blank=True) # Can be used for Magazine ID, etc.

    uploaded_file = models.FileField(upload_to=publication_media_dir, max_length=500)

    original_file_name = models.CharField(max_length=200)
    file_ext = models.CharField(max_length=10)

    uploaded = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, related_name='uploading_publication_uploaded_by')

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = uuid.uuid4()
        super(UploadingPublication, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return '%s.%s (%s.%s)' % (self.original_file_name, self.file_ext, self.uid, self.file_ext)
    
    def can_view(self, user):
        return UserPublisher.objects.filter(user=user, publisher=self.publisher).exists()

class Publication(models.Model):
    PUBLISH_STATUS = {
        'UNPUBLISHED':1,
        'SCHEDULED':2,
        'PUBLISHED':3,
    }

    publisher = models.ForeignKey('Publisher')

    uid = models.CharField(max_length=200, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    publication_type = models.CharField(max_length=50) # Also module_code

    uploaded_file = PrivateFileField(upload_to=publication_media_dir, condition=is_downloadable, max_length=500, null=True)
    original_file_name = models.CharField(max_length=300)
    file_ext = models.CharField(max_length=10)

    publish_status = models.IntegerField(default=PUBLISH_STATUS['UNPUBLISHED'])
    publish_schedule = models.DateTimeField(null=True, blank=True)
    published = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey(User, null=True, blank=True, related_name='publication_published_by')

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
    
    def get_publication_title(self):
        from common.modules import get_publication_module
        return get_publication_module(self.publication_type).get_publication_title(self)
    
    def can_view(self, user):
        return UserPublisher.objects.filter(user=user, publisher=self.publisher).exists()

class PublicationCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


