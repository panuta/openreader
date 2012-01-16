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



from django.db.models.signals import post_syncdb
post_syncdb.connect(after_syncdb, dispatch_uid="common.management")