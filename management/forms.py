# -*- encoding: utf-8 -*-

from django import forms

from common.forms import StrippedCharField

from domain.models import Organization, OrganizationInvitation

class CreateOrganizationForm(forms.Form):
    organization_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span6'}))
    organization_slug = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span6'}))
    organization_prefix = StrippedCharField(max_length=100, widget=forms.TextInput(attrs={'class':'span4'}))
    admin_email = forms.EmailField(widget=forms.TextInput(attrs={'class':'span6'}))

    def clean_organization_slug(self):
        organization_slug = self.cleaned_data['organization_slug']

        if Organization.objects.filter(slug=organization_slug).exists():
            raise forms.ValidationError(u'ชื่อย่อบริษัทนี้ซ้ำกับชื่ออื่นๆ ในระบบ')
        
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
    