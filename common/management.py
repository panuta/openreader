# -*- encoding: utf-8 -*-

import datetime

from django.contrib.sites.models import Site

from accounts.models import *
from publisher.models import *
from publisher.book.models import *
from publisher.magazine.models import *

def after_syncdb(sender, **kwargs):
    
    """
    PRODUCTION CODE
    """

    Site.objects.all().update(domain=settings.WEBSITE_DOMAIN, name=settings.WEBSITE_NAME)

    """
    DEVELOPMENT CODE
    """


    """
    magazine, created = Magazine.objects.get_or_create(publisher=publisher, title='Magazine 1', created_by=admin_user)

    publication, created = Publication.objects.get_or_create(
        publisher=publisher, 
        title='Issue Name 1', 
        publish_status=Publication.STATUS['UNPUBLISHED'], 
        publication_type='magazine',
        original_file_name='a', file_ext='pdf', uploaded_by=admin_user)
    MagazineIssue.objects.get_or_create(magazine=magazine, publication=publication)

    publication, created = Publication.objects.get_or_create(
        publisher=publisher, 
        title='Issue Name 3', 
        publish_status=Publication.STATUS['SCHEDULED'], 
        publication_type='magazine',
        original_file_name='a', file_ext='pdf', uploaded_by=admin_user)
    publication.publish_schedule = datetime.datetime.today()
    publication.published_by = admin_user
    publication.save()
    MagazineIssue.objects.get_or_create(magazine=magazine, publication=publication)

    publication, created = Publication.objects.get_or_create(
        publisher=publisher, 
        title='Issue Name 4', 
        publish_status=Publication.STATUS['PUBLISHED'], 
        publication_type='magazine',
        original_file_name='a', file_ext='pdf', uploaded_by=admin_user)
    publication.published = datetime.datetime.today()
    publication.save()
    MagazineIssue.objects.get_or_create(magazine=magazine, publication=publication)

    publication, created = Publication.objects.get_or_create(
        publisher=publisher, 
        title='Issue Name 5', 
        publish_status=Publication.STATUS['PUBLISHED'], 
        publication_type='magazine',
        original_file_name='a', file_ext='pdf', uploaded_by=admin_user)
    publication.published = datetime.datetime.today()
    publication.save()
    MagazineIssue.objects.get_or_create(magazine=magazine, publication=publication)
    
    """











from django.db.models.signals import post_syncdb
post_syncdb.connect(after_syncdb, dispatch_uid="common.management")