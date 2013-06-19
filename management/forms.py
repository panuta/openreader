# -*- encoding: utf-8 -*-

import re

from django import forms
from django.utils.translation import ugettext

from common.countries import COUNTRY_CHOICES_WITH_BLANK
from common.forms import StrippedCharField

from domain.models import Organization, OrganizationInvitation, OrganizationBanner


class CreateOrganizationForm(forms.Form):
    organization_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span6'}))
    organization_slug = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span6'}))
    organization_prefix = StrippedCharField(max_length=100, widget=forms.TextInput(attrs={'class':'span4'}))
    admin_email = forms.EmailField(widget=forms.TextInput(attrs={'class':'span6'}))

    def clean_organization_slug(self):
        organization_slug = self.cleaned_data['organization_slug']

        if not re.match('^[A-Za-z0-9]*$', organization_slug):
            raise forms.ValidationError(ugettext('Company url name must contains only characters and numbers.'))

        if Organization.objects.filter(slug__iexact=organization_slug).exists() or OrganizationInvitation.objects.filter(organization_slug=organization_slug).exists():
            raise forms.ValidationError(ugettext('This company url name is already exists in the system.'))

        return organization_slug
    
class EditOrganizationForm(forms.Form):
    organization_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span6'}))
    organization_slug = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span6'}))
    organization_prefix = StrippedCharField(max_length=100, widget=forms.TextInput(attrs={'class':'span4'}))

    def __init__(self, organization, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.organization = organization

    def clean_organization_slug(self):
        organization_slug = self.cleaned_data['organization_slug']

        if not re.match('^[A-Za-z0-9]*$', organization_slug):
            raise forms.ValidationError(ugettext('Company url name must contains only characters and numbers.'))

        if Organization.objects.filter(slug=organization_slug).exclude(id=self.organization.id).exists():
            raise forms.ValidationError(u'ชื่อย่อบริษัทนี้ซ้ำกับชื่ออื่นๆ ในระบบ')

        if OrganizationInvitation.objects.filter(organization_slug=organization_slug).exists():
            raise forms.ValidationError(u'ชื่อย่อบริษัทนี้ซ้ำกับชื่ออื่นๆ ในคำขอเพิ่มบริษัท')
        
        return organization_slug


class EditOrganizationInvitationForm(forms.Form):
    organization_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span6'}))
    organization_slug = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span6'}))
    organization_prefix = StrippedCharField(max_length=100, widget=forms.TextInput(attrs={'class':'span4'}))
    
    def __init__(self, invitation, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.invitation = invitation

    def clean_organization_slug(self):
        organization_slug = self.cleaned_data['organization_slug']

        if Organization.objects.filter(slug=organization_slug).exists():
            raise forms.ValidationError(u'ชื่อย่อบริษัทนี้ซ้ำกับชื่ออื่นๆ ในระบบ')

        if OrganizationInvitation.objects.filter(organization_slug=organization_slug).exclude(id=self.invitation.id).exists():
            raise forms.ValidationError(u'ชื่อย่อบริษัทนี้ซ้ำกับชื่ออื่นๆ ในคำขอเพิ่มบริษัท')
        
        return organization_slug


class OrganizationBannerForm(forms.Form):
    organization = forms.ModelChoiceField(queryset=Organization.objects.all())
    order = forms.IntegerField(min_value=0)
    image = forms.ImageField()
    link = forms.URLField(widget=forms.TextInput(attrs={'class':'span6'}))

    def clean(self):
        cleaned_data = super(OrganizationBannerForm, self).clean()

        organization = cleaned_data.get('organization')
        order = cleaned_data.get('order')

        if OrganizationBanner.objects.filter(organization=organization, order=order).exists():
            raise forms.ValidationError(u'This orgnaization and order has already exists.')

        return cleaned_data


class OrganizationKnowledgeForm(forms.Form):
    organization = forms.ModelChoiceField(queryset=Organization.objects.all())
    title = StrippedCharField(max_length=255, widget=forms.TextInput(attrs={'class':'span6'}))
    weight = forms.IntegerField(min_value=0)
    image = forms.ImageField()
    link = forms.URLField(widget=forms.TextInput(attrs={'class':'span6'}))


