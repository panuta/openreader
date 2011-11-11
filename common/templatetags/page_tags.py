# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from django.core.urlresolvers import reverse

from common import utilities

from publication.models import PublisherModule

# UPLOAD PUBLICATION #################################################################


