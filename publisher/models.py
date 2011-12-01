import uuid

from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.db import models
from django.db.models import Q

from private_files import PrivateFileField

from common.modules import get_publication_module

from accounts.models import UserPublisher

def is_downloadable(request, instance):
    return True

def publication_media_dir(instance, filename):
    return '%s%s/%s' % (settings.PUBLICATION_ROOT, instance.publisher.id, filename)

class Module(models.Model):
    module_name = models.CharField(max_length=100) # Use for reference in code
    module_type = models.CharField(max_length=50)
    title = models.CharField(max_length=100) # Use for showing in HTML
    description = models.CharField(max_length=1000, blank=True, null=True)
    front_page_url = models.CharField(max_length=100, null=True)

    def __unicode__(self):
        return '%s:%s' % (self.module_name, self.module_type)
    
    def get_module_object(self, sub_module=''):
        if sub_module:
            sub_module = '.' + sub_module
        
        try:
            return __import__('publisher.%s%s' % (self.module_name, sub_module), fromlist=['publisher'])
        except:
            return None

class Reader(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)

    def __unicode__(self):
        return self.name

class PublicationCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

# Publisher ############################################################

class Publisher(models.Model):
    name = models.CharField(max_length=200)
    status = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='publisher_created_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='publisher_modified_by', null=True, blank=True)

    def __unicode__(self):
        return self.name

    def can_view(self, user):
        return UserPublisher.objects.filter(user=user, publisher=self).exists()

    def can_edit(self, user):
        try:
            user_publisher = UserPublisher.objects.get(publisher=self, user=user)
            return user_publisher.role.code in ('publisher_admin', 'publisher_staff')
        except UserPublisher.DoesNotExist:
            return False
    
    def can_manage(self, user):
        try:
            user_publisher = UserPublisher.objects.get(publisher=self, user=user)
            return user_publisher.role.code in ('publisher_admin', )
        except UserPublisher.DoesNotExist:
            return False

class PublisherModule(models.Model):
    publisher = models.ForeignKey('Publisher')
    module = models.ForeignKey('Module')
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s:%s' % (self.publisher.name, self.module.module_name)
    
    def get_module_object(self, sub_module=''):
        return self.module.get_module_object(sub_module)

class PublisherReader(models.Model):
    publisher = models.ForeignKey('Publisher')
    reader = models.ForeignKey('Reader')
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s:%s' % (self.publisher.name, self.reader.name)

class PublisherShelf(models.Model):
    publisher = models.ForeignKey('Publisher')
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='publisher_shelf_created_by')

    def __unicode__(self):
        return '%s:%s' % (self.publisher.name, self.name)

# Publication ############################################################

class Publication(models.Model):
    STATUS = {
        'UPLOADED':0,
        'UNPUBLISHED':1,
        'SCHEDULED':2,
        'PUBLISHED':3,
    }

    publisher = models.ForeignKey('Publisher')

    uid = models.CharField(max_length=200, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    publication_type = models.CharField(max_length=50) # Also module_name

    uploaded_file = PrivateFileField(upload_to=publication_media_dir, condition=is_downloadable, max_length=500, null=True)
    #uploaded_file = models.FileField(upload_to='/web/sites/openreader/files/', max_length=500, null=True)
    original_file_name = models.CharField(max_length=300)
    file_ext = models.CharField(max_length=10)
    is_processing = models.BooleanField(default=True)

    status = models.IntegerField(default=STATUS['UPLOADED'])
    is_public_listing = models.BooleanField(default=False)

    web_scheduled =  models.DateTimeField(null=True, blank=True)
    web_scheduled_by =  models.ForeignKey(User, null=True, blank=True, related_name='publication_web_scheduled_by')
    web_published =  models.DateTimeField(null=True, blank=True)
    web_published_by = models.ForeignKey(User, null=True, blank=True, related_name='publication_web_published_by')

    uploaded = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, related_name='publication_uploaded_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='publication_modified_by', null=True, blank=True)

    shelves = models.ManyToManyField(PublisherShelf, through='PublicationShelf')
    readers = models.ManyToManyField(Reader, through='PublicationReader')

    def __unicode__(self):
        return '%s' % (self.title)
    
    def get_publication_title(self):
        return get_publication_module(self.publication_type).get_publication_title(self)
    
    def get_publication_type(self):
        return Module.objects.get(module_name=self.publication_type).title

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = uuid.uuid4()
        super(Publication, self).save(*args, **kwargs)
    
    def can_view(self, user):
        return UserPublisher.objects.filter(user=user, publisher=self.publisher).exists()

class PublicationNotice(models.Model):
    NOTICE = {
        'PUBLISH_WHEN_READY':1,
    }

    publication = models.ForeignKey('Publication')
    notice = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

class PublicationShelf(models.Model):
    publication = models.ForeignKey(Publication)
    shelf = models.ForeignKey(PublisherShelf)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='publication_shelf_created_by')

class PublicationReader(models.Model):
    publication = models.ForeignKey(Publication)
    reader = models.ForeignKey(Reader)
    
    scheduled = models.DateTimeField(null=True, blank=True)
    scheduled_by = models.ForeignKey(User, null=True, blank=True, related_name='publication_reader_scheduled_by')

    published = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey(User, null=True, blank=True, related_name='publication_reader_published_by')

