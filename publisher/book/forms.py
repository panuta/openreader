from django import forms

from widgets import YUICalendar, HourMinuteTimeInput

from publisher.forms import GeneralUploadPublicationForm, PublicationCategoryMultipleChoiceField
from publisher.models import Publication

class UploadPublicationForm(GeneralUploadPublicationForm):
    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        forms.Form.__init__(self, *args, **kwargs)

class FinishUploadBookForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'span10'}))
    author = forms.CharField(widget=forms.TextInput(attrs={'class':'span10'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))
    publish_status = forms.ChoiceField(required=False, choices=((Publication.PUBLISH_STATUS['UNPUBLISHED'], 'Unpulished'), (Publication.PUBLISH_STATUS['SCHEDULED'], 'Scheduled'), (Publication.PUBLISH_STATUS['PUBLISHED'], 'Published')))
    schedule_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_schedule_date'}), required=False)
    schedule_time = forms.TimeField(widget=HourMinuteTimeInput(), required=False)

    categories = PublicationCategoryMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple())

    """
    def __init__(self, *args, **kwargs):
        self.publication = kwargs.pop('publication', None)
        forms.Form.__init__(self, *args, **kwargs)
    """
    
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

class EditBookDetailsForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'span10'}))
    author = forms.CharField(widget=forms.TextInput(attrs={'class':'span10'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))

    categories = PublicationCategoryMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple())

class EditBookStatusForm(forms.Form):
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