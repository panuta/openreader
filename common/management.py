# -*- encoding: utf-8 -*-

import datetime

from django.contrib.auth.models import Group

from accounts.models import *
from publication.models import *
from publication.book.models import *
from publication.magazine.models import *

def after_syncdb(sender, **kwargs):
    
    """
    PRODUCTION CODE
    """

    publisher_admin_group, created = Group.objects.get_or_create(name='publisher_admin')
    publisher_staff_group, created = Group.objects.get_or_create(name='publisher_staff')

    """
    DEVELOPMENT CODE
    """

    try:
        admin_user = User.objects.get(username='admin@openreader.com')
        
    except User.DoesNotExist:
        random_password = 'panuta'
        admin_user = User.objects.create_user('admin@openreader.com', 'admin@openreader.com', random_password)
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()

        user_profile = admin_user.get_profile()
        user_profile.first_name = 'Admin'
        user_profile.last_name = 'Openreader'
        user_profile.save()

        admin_user.groups.add(publisher_admin_group)
    
    try:
        staff_user = User.objects.get(username='staff@openreader.com')
        
    except User.DoesNotExist:
        random_password = 'panuta'
        staff_user = User.objects.create_user('staff@openreader.com', 'staff@openreader.com', random_password)

        user_profile = staff_user.get_profile()
        user_profile.first_name = 'Staff'
        user_profile.last_name = 'Openreader'
        user_profile.save()

        staff_user.groups.add(publisher_staff_group)
    
    publisher, created = Publisher.objects.get_or_create(name='Opendream', created_by=admin_user, modified_by=admin_user)
    UserPublisher.objects.get_or_create(user=admin_user, publisher=publisher, is_default=True)

    PublisherModule.objects.get_or_create(publisher=publisher, module_name='magazine', module_type='publication')
    PublisherModule.objects.get_or_create(publisher=publisher, module_name='book', module_type='publication')
    PublisherModule.objects.get_or_create(publisher=publisher, module_name='shelf', module_type='feature')

    """
    magazine, created = Magazine.objects.get_or_create(publisher=publisher, title='Magazine 1', created_by=admin_user)

    publication, created = Publication.objects.get_or_create(
        publisher=publisher, 
        title='Issue Name 1', 
        publish_status=Publication.PUBLISH_STATUS_UNPUBLISHED, 
        publication_type='magazine',
        original_file_name='a', file_ext='pdf', uploaded_by=admin_user)
    MagazineIssue.objects.get_or_create(magazine=magazine, publication=publication)

    publication, created = Publication.objects.get_or_create(
        publisher=publisher, 
        title='Issue Name 2', 
        publish_status=Publication.PUBLISH_STATUS_READY_TO_PUBLISH, 
        publication_type='magazine',
        original_file_name='a', file_ext='pdf', uploaded_by=admin_user)
    publication.publish_schedule = datetime.datetime.today()
    publication.published_by = admin_user
    publication.save()
    MagazineIssue.objects.get_or_create(magazine=magazine, publication=publication)

    publication, created = Publication.objects.get_or_create(
        publisher=publisher, 
        title='Issue Name 3', 
        publish_status=Publication.PUBLISH_STATUS_SCHEDULE_TO_PUBLISH, 
        publication_type='magazine',
        original_file_name='a', file_ext='pdf', uploaded_by=admin_user)
    publication.publish_schedule = datetime.datetime.today()
    publication.published_by = admin_user
    publication.save()
    MagazineIssue.objects.get_or_create(magazine=magazine, publication=publication)

    publication, created = Publication.objects.get_or_create(
        publisher=publisher, 
        title='Issue Name 4', 
        publish_status=Publication.PUBLISH_STATUS_PUBLISHED, 
        publication_type='magazine',
        original_file_name='a', file_ext='pdf', uploaded_by=admin_user)
    publication.published = datetime.datetime.today()
    publication.save()
    MagazineIssue.objects.get_or_create(magazine=magazine, publication=publication)

    publication, created = Publication.objects.get_or_create(
        publisher=publisher, 
        title='Issue Name 5', 
        publish_status=Publication.PUBLISH_STATUS_PUBLISHED, 
        publication_type='magazine',
        original_file_name='a', file_ext='pdf', uploaded_by=admin_user)
    publication.published = datetime.datetime.today()
    publication.save()
    MagazineIssue.objects.get_or_create(magazine=magazine, publication=publication)
    
    """











from django.db.models.signals import post_syncdb
post_syncdb.connect(after_syncdb, dispatch_uid="common.management")