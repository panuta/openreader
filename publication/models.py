# -*- encoding: utf-8 -*-

import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from private_files import PrivateFileField

from common.utilities import format_abbr_datetime

def is_downloadable(request, instance):
    return True

def publication_media_dir(instance, filename):
    return '%s%s/%s' % (settings.PUBLICATION_ROOT, instance.organization.id, filename)

class Publication(models.Model):
    STATUS = {
        'UNPUBLISHED':1,
        'SCHEDULED':2,
        'PUBLISHED':3,
    }

    organization = models.ForeignKey('accounts.Organization')

    uid = models.CharField(max_length=200, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    publication_type = models.CharField(max_length=50) # Also module_name

    uploaded_file = PrivateFileField(upload_to=publication_media_dir, condition=is_downloadable, max_length=500, null=True)
    #uploaded_file = models.FileField(upload_to='/web/sites/openreader/files/', max_length=500, null=True)
    original_file_name = models.CharField(max_length=300)
    file_ext = models.CharField(max_length=10)
    is_processing = models.BooleanField(default=True)

    status = models.IntegerField(default=STATUS['UNPUBLISHED'])
    is_public_listing = models.BooleanField(default=False)

    scheduled =  models.DateTimeField(null=True, blank=True)
    scheduled_by =  models.ForeignKey(User, null=True, blank=True, related_name='publication_scheduled_by')
    published =  models.DateTimeField(null=True, blank=True)
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
    
    def get_status_text(self):
        if self.status == Publication.STATUS['UNPUBLISHED']:
        
            if self.is_processing and PublicationNotice.objects.filter(publication=self, notice=PublicationNotice.NOTICE['PUBLISH_WHEN_READY']).exists():
                return u'<span class="unpublished">ไฟล์จะเผยแพร่ทันทีที่ประมวลผลเสร็จ</span>'
        
            return u'<span class="unpublished">ยังไม่เผยแพร่</span>'

        elif self.status == Publication.STATUS['SCHEDULED']:
            return u'<span class="scheduled">ตั้งเวลาเผยแพร่</span>'
        
        elif self.status == Publication.STATUS['PUBLISHED']:
            return u'<span class="published">เผยแพร่แล้ว</span>'
        
        return ''
    
    def is_publish_when_ready(self):
        return PublicationNotice.objects.filter(publication=self, notice=PublicationNotice.NOTICE['PUBLISH_WHEN_READY']).exists()

class PublicationNotice(models.Model):
    NOTICE = {
        'PUBLISH_WHEN_READY':1,
    }

    publication = models.ForeignKey(Publication)
    notice = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

class UserPurchasedPublication(models.Model):
    user = models.ForeignKey(User)
    publication = models.ForeignKey(Publication)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s:%s' % (self.user.get_profile().get_fullname(), self.publication.uid)
