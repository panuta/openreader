from django import forms
from django.utils.translation import ugettext_lazy as _

from common.forms import StrippedCharField
from widgets import YUICalendar, HourMinuteTimeInput

from publisher.forms import GeneralUploadPublicationForm, PublicationCategoryMultipleChoiceField

from publisher.models import Publication
from publisher.magazine.models import Magazine

class PublisherMagazineChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['empty_label'] = ''
        kwargs['queryset'] = Magazine.objects.all().order_by('title')
        forms.ModelChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return '%s' % (obj.title)


class UploadPublicationForm(GeneralUploadPublicationForm):
    magazine = PublisherMagazineChoiceField(required=False)
    magazine_name = StrippedCharField(required=False)

    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        forms.Form.__init__(self, *args, **kwargs)

        self.fields['magazine'].queryset = Magazine.objects.filter(publisher=self.publisher).order_by('title')
    
    def after_upload(self, request, uploading_publication):
        if self.cleaned_data['magazine_name']:
            magazine = Magazine.objects.create(publisher=uploading_publication.publisher, title=self.cleaned_data['magazine_name'], created_by=request.user)
        else:
            magazine = self.cleaned_data['magazine']
        uploading_publication.parent_id = magazine.id
        uploading_publication.save()

class FinishUploadMagazineIssueForm(forms.Form):
    magazine = PublisherMagazineChoiceField(required=False)
    title = StrippedCharField(widget=forms.TextInput(attrs={'class':'span10'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))
    publish_status = forms.ChoiceField(required=False, choices=((Publication.PUBLISH_STATUS['UNPUBLISHED'], 'Unpulished'), (Publication.PUBLISH_STATUS['SCHEDULED'], 'Scheduled'), (Publication.PUBLISH_STATUS['PUBLISHED'], 'Published')))
    schedule_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_schedule_date'}), required=False)
    schedule_time = forms.TimeField(widget=HourMinuteTimeInput(), required=False)

    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        self.uploading_publication = kwargs.pop('uploading_publication', None)
        forms.Form.__init__(self, *args, **kwargs)

        self.fields['magazine'].queryset = Magazine.objects.filter(publisher=self.publisher).order_by('title')
    
    def clean_magazine(self):
        data = self.cleaned_data.get('magazine')
        if not self.uploading_publication.parent_id and not data:
            raise forms.ValidationError(_(u'This field is required.'))
        
        return data
    
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
    title = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span9', 'rows':'3'}))
    categories = PublicationCategoryMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple())

class EditMagazineIssueDetailsForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'span10'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))

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
