# -*- encoding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from widgets import YUICalendar, HourMinuteTimeInput

from common.forms import StrippedCharField
from common.permissions import ROLE_CHOICES

from publisher.models import PublicationCategory

class PublicationCategoryMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = PublicationCategory.objects.all().order_by('name')
        forms.ModelMultipleChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return '%s' % (obj.name)

# Publication
