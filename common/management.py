# -*- encoding: utf-8 -*-

from accounts.models import *
from publication.models import * 

def after_syncdb(sender, **kwargs):
    try:
        admin_user = User.objects.get(username='panuta')
        
    except User.DoesNotExist:
        random_password = 'panuta'
        admin_user = User.objects.create_user('panuta', 'panuta@gmail.com', random_password)
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
    
    publisher, created = Publisher.objects.get_or_create(name='Opendream', created_by=admin_user, modified_by=admin_user)
    UserPublisher.objects.get_or_create(user=admin_user, publisher=publisher, is_default=True)


from django.db.models.signals import post_syncdb
post_syncdb.connect(after_syncdb, dispatch_uid="sample_app.management")