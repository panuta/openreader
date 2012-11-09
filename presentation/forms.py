# -*- encoding: utf-8 -*-

import re

from django import forms
from django.contrib.auth.models import User
from django.core.validators import email_re
from django.utils.translation import ugettext, ugettext_lazy as _

from common.countries import COUNTRY_CHOICES_WITH_BLANK
from common.forms import StrippedCharField

from domain.models import OrganizationGroup, UserOrganizationInvitation, UserOrganization, OrganizationAdminPermission, OrganizationShelf, Organization, OrganizationInvitation

# USER ACCOUNT #########################################################################################################

class OrganizationGroupMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = OrganizationGroup.objects.all()
        kwargs['widget'] = forms.SelectMultiple(attrs={'data-placeholder':_('Select group'), 'style':'width:500px;'}) # Use for 'Chosen' jQuery plugin
        forms.ModelMultipleChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return obj.name


class UserProfileForm(forms.Form):
    first_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'input-normal'}))
    last_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'input-normal'}))

    def __init__(self, user, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)

        self.user = user


# ORGANIZATION MANAGEMENT

class OrganizationRegisterForm(forms.Form):
    organization_name = StrippedCharField(max_length=200)
    organization_slug = forms.CharField(max_length=200)
    organization_address = StrippedCharField(max_length=500)
    organization_country = forms.ChoiceField(choices=COUNTRY_CHOICES_WITH_BLANK, widget=forms.Select(attrs={'style':'width:110px;'}))
    organization_tel = StrippedCharField(max_length=30)
    organization_email = forms.EmailField(widget=forms.TextInput(attrs={'class':'span6'}))

    admin_email = forms.EmailField(widget=forms.TextInput(attrs={'class':'span6'}))

    def clean_organization_slug(self):
        organization_slug = self.cleaned_data['organization_slug']

        if not re.match('^[A-Za-z0-9]*$', organization_slug):
            raise forms.ValidationError(ugettext('Company url name must contains only characters and numbers.'))

        if Organization.objects.filter(slug=organization_slug).exists() or OrganizationInvitation.objects.filter(organization_slug=organization_slug).exists():
            raise forms.ValidationError(ugettext('This company url name is already exists in the system.'))

        return organization_slug


class AddOrganizationUserForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'input-normal'}))
    first_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'input-normal'}))
    last_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'input-normal'}))
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    id_no = StrippedCharField(max_length=30, widget=forms.TextInput(attrs={'class':'input-normal'}))
    country = forms.ChoiceField(choices=COUNTRY_CHOICES_WITH_BLANK, widget=forms.Select(attrs={'style':'width:200px;'}))

    groups = OrganizationGroupMultipleChoiceField(required=False)

    def __init__(self, organization, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)

        self.organization = organization
        self.fields['groups'].queryset = OrganizationGroup.objects.filter(organization=organization).order_by('name')

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(ugettext('This email is already exists.'))
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError(ugettext('The two password fields didn\'t match.'))
        return password2


class InviteOrganizationUserForm(forms.Form):
    emails = forms.CharField(widget=forms.Textarea(attrs={'class':'input-large', 'rows':'3'}))
    groups = OrganizationGroupMultipleChoiceField(required=False)

    def __init__(self, organization, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)

        self.organization = organization
        self.fields['groups'].queryset = OrganizationGroup.objects.filter(organization=organization).order_by('name')

    def clean_emails(self):
        saved_emails = self.cleaned_data.get('emails', '')
        saved_emails = [saved_email.strip() for saved_email in saved_emails.split(',') if len(saved_email.strip())>0]
        emails = list(set(saved_emails))
        
        for email in emails:
            if not email_re.match(email):
                raise forms.ValidationError(_('%s is invalid email.') % email)

            if UserOrganizationInvitation.objects.filter(email=email, organization=self.organization).exists():
                raise forms.ValidationError(ugettext('There has already invited to this user.'))

            if UserOrganization.objects.filter(organization=self.organization, user__email=email).exists():
                raise forms.ValidationError(ugettext('This user is already in this organization.'))

        return emails


class EditOrganizationUserInviteForm(forms.Form):
    groups = OrganizationGroupMultipleChoiceField(required=False)

    def __init__(self, organization, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)

        self.organization = organization
        self.fields['groups'].queryset = OrganizationGroup.objects.filter(organization=organization).order_by('name')


class ClaimOrganizationUserForm(forms.Form):
    first_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'input-normal'}))
    last_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'input-normal'}))
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError(ugettext('The two password fields didn\'t match.'))
        return password2


class ClaimOrganizationUserAdminForm(forms.Form):
    first_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'input-normal'}))
    last_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'input-normal'}))
    password1 = forms.CharField(widget=forms.PasswordInput(), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(), required=False)
    id_no = StrippedCharField(max_length=30, widget=forms.TextInput(attrs={'class':'input-normal'}))
    country = forms.ChoiceField(choices=COUNTRY_CHOICES_WITH_BLANK, widget=forms.Select(attrs={'style':'width:200px;'}))

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError(ugettext('The two password fields didn\'t match.'))
        return password2


class ClaimOrganizationExistUserAdminForm(forms.Form):
    first_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'input-normal'}))
    last_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'input-normal'}))
    id_no = StrippedCharField(max_length=30, widget=forms.TextInput(attrs={'class':'input-normal'}))
    country = forms.ChoiceField(choices=COUNTRY_CHOICES_WITH_BLANK, widget=forms.Select(attrs={'style':'width:200px;'}))


class EditOrganizationUserForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'input-normal'}))
    first_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'input-normal'}))
    last_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'input-normal'}))
    groups = OrganizationGroupMultipleChoiceField(required=False)

    def __init__(self, user_organization, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)

        self.user_organization = user_organization
        self.fields['groups'].queryset = OrganizationGroup.objects.filter(organization=user_organization.organization).order_by('name')

    def clean_email(self):
        email = self.cleaned_data.get('email', '')

        if User.objects.filter(email=email).exclude(id=self.user_organization.user.id).exists():
            raise forms.ValidationError(ugettext('This email is already exists.'))

        return email


class OrganizationGroupForm(forms.Form):
    name = StrippedCharField(max_length=100, widget=forms.TextInput(attrs={'class':'input-normal'}))
    description = StrippedCharField(required=False, max_length=500, widget=forms.Textarea(attrs={'class':'input-large', 'rows':'3'}))
    admin_permissions = forms.ModelMultipleChoiceField(required=False, queryset=OrganizationAdminPermission.objects.all(), widget=forms.CheckboxSelectMultiple())


# DOCUMENT #############################################################################################################

class OrganizationShelfMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = OrganizationShelf.objects.all().order_by('name')
        forms.ModelMultipleChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return '%s' % (obj.name)


class OrganizationShelfForm(forms.Form):
    name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'input-normal'}))
    auto_sync = forms.BooleanField(required=False)
    archive = forms.BooleanField(required=False)
    shelf_icon = forms.CharField(max_length=100)

