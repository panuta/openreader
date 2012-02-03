# -*- encoding: utf-8 -*-

from django import forms

from common.forms import StrippedCharField

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
    shelf_icon = forms.CharField(max_length=100)
    permission = forms.CharField()
