from django import forms
from django.utils.translation import ugettext_lazy as _

from widgets import YUICalendar, HourOnlyTimeInput

from common.forms import StrippedCharField

from publication.models import Publisher, PublicationCategory
from publication.magazine.models import Magazine

class PublisherMagazineChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['empty_label'] = ''
        kwargs['queryset'] = Magazine.objects.all().order_by('title')
        forms.ModelChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return '%s' % (obj.title)

# Form classes

class PublisherForm(forms.Form):
    name = StrippedCharField()

class GeneralUploadPublicationForm(forms.Form):
    module = forms.CharField(widget=forms.HiddenInput(), max_length=50)
    publication = forms.FileField()

    def clean(self):
        cleaned_data = self.cleaned_data
        # TODO: Check eligible file type from all available modules
        return cleaned_data
    
    def persist(self, uploading_publication):
        pass

class MagazineIssueForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'span10'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))

class PublicationStatusForm(forms.Form):
    publish_status = forms.ChoiceField(choices=(('unpublished', 'Unpulished'), ('scheduled', 'Scheduled'), ('published', 'Published')))
    schedule_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_schedule_date'}), required=False)
    schedule_time = forms.TimeField(widget=HourOnlyTimeInput(), required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        publish_status = cleaned_data.get('publish_status')
        schedule_date = cleaned_data.get('schedule_date')
        schedule_time = cleaned_data.get('schedule_time')

        if publish_status == 'scheduled' and not (schedule_date or schedule_time):
            self._errors['publish_status'] = self.error_class([_(u'This field is required.')])
        
        return cleaned_data


# Publisher Management

class PublisherProfileForm(forms.Form):
    name = forms.CharField(max_length=200)

class PublisherShelfForm(forms.Form):
    name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))
    description = StrippedCharField(widget=forms.Textarea(attrs={'class':'span9', 'rows':'3'}))

# class FinishUploadPictureForm(forms.Form):
#     title = forms.CharField()
#     description = forms.CharField(required=False, widget=forms.Textarea)