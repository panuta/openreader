# -*- encoding: utf-8 -*-

from django import forms

from publisher.forms import GeneralUploadPublicationForm, PublisherShelfMultipleChoiceField, EditPublicationForm
from publisher.models import Publication, PublisherShelf, PublicationShelf

from common.forms import StrippedCharField
from common.modules import has_module

class UploadPublicationForm(GeneralUploadPublicationForm):
    shelf = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        forms.Form.__init__(self, *args, **kwargs)
    
    def after_upload(self, request, publication):
        if self.cleaned_data['shelf']:
            try:
                shelf = PublisherShelf.objects.get(id=self.cleaned_data['shelf'])
            except PublisherShelf.DoesNotExist:
                pass
            else:
                PublicationShelf.objects.create(publication=publication, shelf=shelf, created_by=request.user)

class FinishUploadFileForm(forms.Form):
    next = forms.CharField(required=False, widget=forms.HiddenInput())
    title = StrippedCharField(widget=forms.TextInput(attrs={'class':'span10'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))
    shelf = PublisherShelfMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        forms.Form.__init__(self, *args, **kwargs)

        if has_module(self.publisher, 'shelf'):
            self.fields['shelf'].queryset = PublisherShelf.objects.filter(publisher=self.publisher).order_by('name')

class EditFilePublicationForm(EditPublicationForm):
    shelf = PublisherShelfMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        forms.Form.__init__(self, *args, **kwargs)

        if has_module(self.publisher, 'shelf'):
            self.fields['shelf'].queryset = PublisherShelf.objects.filter(publisher=self.publisher).order_by('name')
