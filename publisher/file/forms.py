from django import forms

from widgets import YUICalendar, HourMinuteTimeInput

from publisher.forms import GeneralUploadPublicationForm, PublisherShelfMultipleChoiceField
from publisher.models import Publication

from common.forms import StrippedCharField
from common.modules import has_module

class UploadPublicationForm(GeneralUploadPublicationForm):
    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        forms.Form.__init__(self, *args, **kwargs)

class FinishUploadFileForm(forms.Form):
    title = StrippedCharField(widget=forms.TextInput(attrs={'class':'span10'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))
    shelf = PublisherShelfMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple())
    publish_status = forms.ChoiceField(choices=((Publication.PUBLISH_STATUS['UNPUBLISHED'], 'Unpulished'), (Publication.PUBLISH_STATUS['SCHEDULED'], 'Scheduled'), (Publication.PUBLISH_STATUS['PUBLISHED'], 'Published')))
    schedule_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_schedule_date'}), required=False)
    schedule_time = forms.TimeField(widget=HourMinuteTimeInput(), required=False)

    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        forms.Form.__init__(self, *args, **kwargs)

        if has_module(publisher, 'shelf'):
            self.fields['shelf'].queryset = PublisherShelf.objects.filter(publisher=self.publisher).order_by('name')

    def clean(self):
        cleaned_data = self.cleaned_data
        publish_status = cleaned_data.get('publish_status')
        schedule_date = cleaned_data.get('schedule_date')
        schedule_time = cleaned_data.get('schedule_time')

        if publish_status == str(Publication.PUBLISH_STATUS['SCHEDULED']) and not schedule_date:
            self._errors['schedule_date'] = self.error_class([_(u'This field is required.')])
        
        if publish_status == str(Publication.PUBLISH_STATUS['SCHEDULED']) and not schedule_time:
            self._errors['schedule_time'] = self.error_class([_(u'This field is required.')])
        
        return cleaned_data

class EditFileDetailsForm(forms.Form):
    title = StrippedCharField(widget=forms.TextInput(attrs={'class':'span10'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))
    shelf = PublisherShelfMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        forms.Form.__init__(self, *args, **kwargs)

        if has_module(publisher, 'shelf'):
            self.fields['shelf'].queryset = PublisherShelf.objects.filter(publisher=self.publisher).order_by('name')

class EditFileStatusForm(forms.Form):
    publish_status = forms.ChoiceField(required=False, choices=((Publication.PUBLISH_STATUS['UNPUBLISHED'], 'Unpulished'), (Publication.PUBLISH_STATUS['SCHEDULED'], 'Scheduled'), (Publication.PUBLISH_STATUS['PUBLISHED'], 'Published')))
    schedule_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_schedule_date'}), required=False)
    schedule_time = forms.TimeField(widget=HourMinuteTimeInput(), required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        publish_status = cleaned_data.get('publish_status')
        schedule_date = cleaned_data.get('schedule_date')
        schedule_time = cleaned_data.get('schedule_time')

        if publish_status == str(Publication.PUBLISH_STATUS['SCHEDULED']) and not schedule_date:
            self._errors['schedule_date'] = self.error_class([_(u'This field is required.')])
        
        if publish_status == str(Publication.PUBLISH_STATUS['SCHEDULED']) and not schedule_time:
            self._errors['schedule_time'] = self.error_class([_(u'This field is required.')])
        
        return cleaned_data