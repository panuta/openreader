from django import forms

from publisher.forms import GeneralUploadPublicationForm, PublicationCategoryMultipleChoiceField
from publisher.models import Publication

from common.forms import StrippedCharField

class UploadPublicationForm(GeneralUploadPublicationForm):
    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        forms.Form.__init__(self, *args, **kwargs)

class FinishUploadBookForm(forms.Form):
    next = forms.CharField(required=False, widget=forms.HiddenInput())
    title = StrippedCharField(widget=forms.TextInput(attrs={'class':'span10'}))
    author = StrippedCharField(widget=forms.TextInput(attrs={'class':'span10'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))

    categories = PublicationCategoryMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple())

class EditBookDetailsForm(forms.Form):
    title = StrippedCharField(widget=forms.TextInput(attrs={'class':'span10'}))
    author = StrippedCharField(widget=forms.TextInput(attrs={'class':'span10'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))

    categories = PublicationCategoryMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple())
