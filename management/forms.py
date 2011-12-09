# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from common.forms import StrippedCharField

from accounts.models import Organization

class CreateOrganizationForm(forms.Form):
    organization_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span6'}))
    admin_email = forms.EmailField(widget=forms.TextInput(attrs={'class':'span6'}))

    def clean_publisher_name(self):
        organization_name = self.cleaned_data['organization_name']

        if Organization.objects.filter(name=organization_name).exists():
            raise forms.ValidationError(u'ชื่อสำนักพิมพ์นี้ซ้ำกับชื่ออื่นๆ ในระบบ')
        
        return organization_name
    