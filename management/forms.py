# -*- encoding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from common.forms import StrippedCharField

from accounts.models import Organization

class CreateOrganizationForm(forms.Form):
    organization_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span6'}))
    organization_slug = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span6'}))
    organization_prefix = StrippedCharField(max_length=100, widget=forms.TextInput(attrs={'class':'span4'}))
    admin_email = forms.EmailField(widget=forms.TextInput(attrs={'class':'span6'}))

    def clean_publisher_name(self):
        organization_slug = self.cleaned_data['organization_slug']

        if Organization.objects.filter(slug=organization_slug).exists():
            raise forms.ValidationError(u'ชื่อย่อบริษัทนี้ซ้ำกับชื่ออื่นๆ ในระบบ')
        
        return organization_name
    