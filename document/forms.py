# -*- encoding: utf-8 -*-

from django import forms

from common.forms import StrippedCharField

from publication.forms import EditPublicationForm

from models import OrganizationShelf

class OrganizationShelfMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = OrganizationShelf.objects.all().order_by('name')
        forms.ModelMultipleChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return '%s' % (obj.name)

class OrganizationShelfForm(forms.Form):
    name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))
    auto_sync = forms.BooleanField(required=False)

class EditFilePublicationForm(EditPublicationForm):
    shelves = OrganizationShelfMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop('organization', None)
        forms.Form.__init__(self, *args, **kwargs)
        
        self.fields['shelves'].queryset = OrganizationShelf.objects.filter(organization=self.organization).order_by('name')
