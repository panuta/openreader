from django import forms
from django.utils.translation import ugettext_lazy as _

from widgets import YUICalendar, HourOnlyTimeInput

from common.forms import StrippedCharField

from publication.models import Publisher, PublicationCategory

class PublicationCategoryMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        
        kwargs['queryset'] = PublicationCategory.objects.all().order_by('name')
        forms.ModelMultipleChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return '%s' % (obj.name)

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
    
    def after_upload(self, uploading_publication):
        pass

# Publisher Management

class PublisherProfileForm(forms.Form):
    name = StrippedCharField(max_length=200)

class PublisherShelfForm(forms.Form):
    name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span9', 'rows':'3'}))

# class FinishUploadPictureForm(forms.Form):
#     title = forms.CharField()
#     description = forms.CharField(required=False, widget=forms.Textarea)