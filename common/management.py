# -*- encoding: utf-8 -*-

import datetime

from django.contrib.auth.models import Group
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

    # Module
    magazine_module, created = Module.objects.get_or_create(module_name='magazine', module_type='publication', title='นิตยสาร', front_page_url='view_magazines')
    book_module, created = Module.objects.get_or_create(module_name='book', module_type='publication', title='หนังสือ', front_page_url='view_books')
    shelf_module, created = Module.objects.get_or_create(module_name='shelf', module_type='feature', title='ชั้นหนังสือ')

    # Roles and Permissions
    publisher_admin_group, created = Group.objects.get_or_create(name='publisher_admin')
    publisher_staff_group, created = Group.objects.get_or_create(name='publisher_staff')
    publisher_user_group, created = Group.objects.get_or_create(name='publisher_user')

    # Publication Categories
    PublicationCategory.objects.get_or_create(name='ท่องเที่ยว', slug='travel')
    PublicationCategory.objects.get_or_create(name='กีฬา', slug='sports')
    PublicationCategory.objects.get_or_create(name='ไลฟ์สไตล์ผู้หญิง', slug='women')
    PublicationCategory.objects.get_or_create(name='สุขภาพ', slug='health')
    PublicationCategory.objects.get_or_create(name='เทคโนโลยี', slug='technology')
    PublicationCategory.objects.get_or_create(name='ไลฟ์สไตล์ผู้ชาย', slug='men')
    PublicationCategory.objects.get_or_create(name='ข่าว', slug='news')
    PublicationCategory.objects.get_or_create(name='แฟชั่น', slug='fashion')
    PublicationCategory.objects.get_or_create(name='ไลฟ์สไตล์ทั่วไป', slug='lifestyle')
    PublicationCategory.objects.get_or_create(name='วัยรุ่น', slug='teenager')
    PublicationCategory.objects.get_or_create(name='นางแบบ', slug='modelling')
    PublicationCategory.objects.get_or_create(name='วงการบันเทิง', slug='gossip')
    PublicationCategory.objects.get_or_create(name='ธรรมมะ', slug='buddhism')
    PublicationCategory.objects.get_or_create(name='แต่งบ้าน', slug='home')
    PublicationCategory.objects.get_or_create(name='บ้านและที่ดิน', slug='land')
    PublicationCategory.objects.get_or_create(name='ยานพาหนะ', slug='vehicle')
    PublicationCategory.objects.get_or_create(name='การออกแบบ', slug='design')
    PublicationCategory.objects.get_or_create(name='แม่และเด็ก', slug='mothor')
    PublicationCategory.objects.get_or_create(name='อาหาร', slug='food')
    PublicationCategory.objects.get_or_create(name='สัตว์เลี้ยง', slug='pet')
    PublicationCategory.objects.get_or_create(name='ช็อปปิ้ง', slug='shopping')
    PublicationCategory.objects.get_or_create(name='ภาพยนต์', slug='movie')
    PublicationCategory.objects.get_or_create(name='เพลงและดนตรี', slug='music')
    PublicationCategory.objects.get_or_create(name='ความรู้ทั่วไป', slug='knowledge')
    PublicationCategory.objects.get_or_create(name='การตลาด', slug='marketing')
    PublicationCategory.objects.get_or_create(name='การเงิน', slug='finance')
    PublicationCategory.objects.get_or_create(name='ธุรกิจทั่วไป', slug='business')
    PublicationCategory.objects.get_or_create(name='การศึกษา', slug='education')
    PublicationCategory.objects.get_or_create(name='ธรรมชาติและสิ่งแวดล้อม', slug='nature')
    PublicationCategory.objects.get_or_create(name='เครื่องประดับ', slug='jewelry')
    PublicationCategory.objects.get_or_create(name='เด็กและเยาวชน', slug='kid')
    PublicationCategory.objects.get_or_create(name='ละครทีวี', slug='tv')
    PublicationCategory.objects.get_or_create(name='เกม', slug='game')

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
        user_profile.is_publisher = True
        user_profile.save()

    try:
        staff_user = User.objects.get(username='staff@openreader.com')
        
    except User.DoesNotExist:
        random_password = 'panuta'
        staff_user = User.objects.create_user('staff@openreader.com', 'staff@openreader.com', random_password)

        user_profile = staff_user.get_profile()
        user_profile.first_name = 'Staff'
        user_profile.last_name = 'Openreader'
        user_profile.is_publisher = True
        user_profile.save()

    try:
        normal_user = User.objects.get(username='panuta@gmail.com')
        
    except User.DoesNotExist:
        random_password = 'panuta'
        normal_user = User.objects.create_user('panuta@gmail.com', 'panuta@gmail.com', random_password)

        user_profile = normal_user.get_profile()
        user_profile.first_name = 'Panu'
        user_profile.last_name = 'Tangchalermkul'
        user_profile.is_publisher = True
        user_profile.save()

    publisher, created = Publisher.objects.get_or_create(name='Opendream', created_by=admin_user, modified_by=admin_user)
    UserPublisher.objects.get_or_create(user=admin_user, publisher=publisher, role=publisher_admin_group, is_default=True)
    UserPublisher.objects.get_or_create(user=staff_user, publisher=publisher, role=publisher_staff_group, is_default=True)
    UserPublisher.objects.get_or_create(user=normal_user, publisher=publisher, role=publisher_user_group, is_default=True)
    
    PublisherModule.objects.get_or_create(publisher=publisher, module=magazine_module)
    PublisherModule.objects.get_or_create(publisher=publisher, module=book_module)
    PublisherModule.objects.get_or_create(publisher=publisher, module=shelf_module)

    """
    magazine, created = Magazine.objects.get_or_create(publisher=publisher, title='Magazine 1', created_by=admin_user)

    publication, created = Publication.objects.get_or_create(
        publisher=publisher, 
        title='Issue Name 1', 
        publish_status=Publication.PUBLISH_STATUS['UNPUBLISHED'], 
        publication_type='magazine',
        original_file_name='a', file_ext='pdf', uploaded_by=admin_user)
    MagazineIssue.objects.get_or_create(magazine=magazine, publication=publication)

    publication, created = Publication.objects.get_or_create(
        publisher=publisher, 
        title='Issue Name 3', 
        publish_status=Publication.PUBLISH_STATUS['SCHEDULED'], 
        publication_type='magazine',
        original_file_name='a', file_ext='pdf', uploaded_by=admin_user)
    publication.publish_schedule = datetime.datetime.today()
    publication.published_by = admin_user
    publication.save()
    MagazineIssue.objects.get_or_create(magazine=magazine, publication=publication)

    publication, created = Publication.objects.get_or_create(
        publisher=publisher, 
        title='Issue Name 4', 
        publish_status=Publication.PUBLISH_STATUS['PUBLISHED'], 
        publication_type='magazine',
        original_file_name='a', file_ext='pdf', uploaded_by=admin_user)
    publication.published = datetime.datetime.today()
    publication.save()
    MagazineIssue.objects.get_or_create(magazine=magazine, publication=publication)

    publication, created = Publication.objects.get_or_create(
        publisher=publisher, 
        title='Issue Name 5', 
        publish_status=Publication.PUBLISH_STATUS['PUBLISHED'], 
        publication_type='magazine',
        original_file_name='a', file_ext='pdf', uploaded_by=admin_user)
    publication.published = datetime.datetime.today()
    publication.save()
    MagazineIssue.objects.get_or_create(magazine=magazine, publication=publication)
    
    """











from django.db.models.signals import post_syncdb
post_syncdb.connect(after_syncdb, dispatch_uid="common.management")