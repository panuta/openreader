# -*- encoding: utf-8 -*-

from django.conf import settings
from django.contrib.sites.models import Site

def after_syncdb(sender, **kwargs):

    """
    PRODUCTION CODE
    """
    Site.objects.all().update(domain=settings.WEBSITE_DOMAIN, name=settings.WEBSITE_NAME)

from django.db.models.signals import post_syncdb
post_syncdb.connect(after_syncdb, dispatch_uid="common.management")