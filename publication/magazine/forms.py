from django import forms
from django.utils.translation import ugettext_lazy as _

from widgets import YUICalendar, HourOnlyTimeInput, HourMinuteTimeInput

from publication.forms import GeneralUploadPublicationForm
from publication.magazine.models import Magazine

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
    
    def persist(self, uploading_publication):
        magazine = self.cleaned_data['magazine']

        uploading_publication.parent_id = magazine.id
        uploading_publication.save()

class FinishUploadMagazineIssueForm(forms.Form):
    magazine = PublisherMagazineChoiceField(required=False)
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'span10'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))
    publish_status = forms.ChoiceField(choices=(('unpublished', 'Unpulished'), ('scheduled', 'Scheduled'), ('published', 'Published')))
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

        if publish_status == 'scheduled' and not schedule_date:
            self._errors['schedule_date'] = self.error_class([_(u'This field is required.')])

        if publish_status == 'scheduled' and not schedule_time:
            self._errors['schedule_time'] = self.error_class([_(u'This field is required.')])
        
        return cleaned_data