from django import forms
from django.utils.translation import ugettext_lazy as _

from common.forms import StrippedCharField
from widgets import YUICalendar, HourMinuteTimeInput

from publisher.forms import GeneralUploadPublicationForm, PublicationCategoryMultipleChoiceField

from publisher.models import Publication
from publisher.magazine.models import Magazine, MagazineIssue, ToCreateMagazine

class PublisherMagazineChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['empty_label'] = ''
        kwargs['queryset'] = Magazine.objects.all().order_by('title')
        forms.ModelChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return '%s' % (obj.title)


class UploadPublicationForm(GeneralUploadPublicationForm):
    magazine = PublisherMagazineChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        forms.Form.__init__(self, *args, **kwargs)

        self.fields['magazine'].queryset = Magazine.objects.filter(publisher=self.publisher).order_by('title')
    
    def after_upload(self, request, publication):
        if self.cleaned_data['magazine']:
            magazine_issue = MagazineIssue.objects.create(publication=publication, magazine=magazine)
        else:
            try:
                ToCreateMagazine.objects.get(publication=publication)
            except ToCreateMagazine.DoesNotExist:
                ToCreateMagazine.objects.create(publication=publication)

class FinishUploadMagazineIssueForm(forms.Form):
    magazine = PublisherMagazineChoiceField(required=False)
    magazine_name = StrippedCharField(required=False, widget=forms.TextInput(attrs={'class':'span8'}))
    categories = PublicationCategoryMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple())

    title = StrippedCharField(widget=forms.TextInput(attrs={'class':'span8'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))
    publish_status = forms.ChoiceField(choices=((Publication.PUBLISH_STATUS['UNPUBLISHED'], 'Unpulished'), (Publication.PUBLISH_STATUS['SCHEDULED'], 'Scheduled'), (Publication.PUBLISH_STATUS['PUBLISHED'], 'Published')))
    schedule_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_schedule_date'}), required=False)
    schedule_time = forms.TimeField(widget=HourMinuteTimeInput(), required=False)

    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        self.publication = kwargs.pop('publication', None)
        self.to_create_magazine = kwargs.pop('to_create_magazine', None)
        forms.Form.__init__(self, *args, **kwargs)

        self.fields['magazine'].queryset = Magazine.objects.filter(publisher=self.publisher).order_by('title')
    
    def clean_magazine(self):
        magazine = self.cleaned_data['magazine']
        if not self.to_create_magazine and not magazine:
            raise forms.ValidationError(_(u'This field is required.'))
        
        return magazine
    
    def clean_magazine_name(self):
        magazine_name = self.cleaned_data['magazine_name']
        if self.to_create_magazine and not magazine_name:
            raise forms.ValidationError(_(u'This field is required.'))
        
        return magazine_name
    
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

class MagazineForm(forms.Form):
    title = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span8'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'3'}))
    categories = PublicationCategoryMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple())

class EditMagazineIssueDetailsForm(forms.Form):
    title = StrippedCharField(widget=forms.TextInput(attrs={'class':'span8'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))

class EditMagazineIssueStatusForm(forms.Form):
    publish_status = forms.ChoiceField(choices=((Publication.PUBLISH_STATUS['UNPUBLISHED'], 'Unpulished'), (Publication.PUBLISH_STATUS['SCHEDULED'], 'Scheduled'), (Publication.PUBLISH_STATUS['PUBLISHED'], 'Published')))
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
