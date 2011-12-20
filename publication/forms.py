# -*- encoding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from widgets import YUICalendar, HourMinuteTimeInput

from common.forms import StrippedCharField

from accounts.models import Organization

class PublicationStatusField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = (('unpublish', 'ยังไม่เผยแพร่'), ('schedule', 'ตั้งเวลาเผยแพร่'), ('publish', 'เผยแพร่'))
        forms.ChoiceField.__init__(self, *args, **kwargs)

# Publication

class EditPublicationForm(forms.Form):
    title = StrippedCharField(widget=forms.TextInput(attrs={'class':'span8'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))
    from_page = forms.CharField(required=False, widget=forms.HiddenInput())

class EditPublicationStatusForm(forms.Form):
    status = PublicationStatusField()
    schedule_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_schedule_date'}), required=False)
    schedule_time = forms.TimeField(widget=HourMinuteTimeInput(), required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        status = cleaned_data.get('status')
        schedule_date = cleaned_data.get('schedule_date')
        schedule_time = cleaned_data.get('schedule_time')

        if status == 'schedule' and not schedule_date:
            self._errors['schedule_date'] = self.error_class([_(u'This field is required.')])
        
        if status == 'schedule' and not schedule_time:
            self._errors['schedule_time'] = self.error_class([_(u'This field is required.')])
        
        return cleaned_data
