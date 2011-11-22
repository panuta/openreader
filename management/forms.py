# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from common.forms import StrippedCharField

from publisher.forms import ModuleMultipleChoiceField
from publisher.models import Publisher

class CreatePublisherForm(forms.Form):
    publisher_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span6'}))
    modules = ModuleMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple())
    admin_email = forms.EmailField(widget=forms.TextInput(attrs={'class':'span6'}))

    def clean_publisher_name(self):
        publisher_name = self.cleaned_data['publisher_name']

        if Publisher.objects.filter(name=publisher_name).exists():
            raise forms.ValidationError(u'ชื่อสำนักพิมพ์นี้ซ้ำกับชื่ออื่นๆ ในระบบ')
        
        return publisher_name
    