# -*- encoding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from common.forms import StrippedCharField

from domain.models import OrganizationGroup, UserOrganizationInvitation, UserOrganization, OrganizationAdminPermission, OrganizationShelf

# USER ACCOUNT #########################################################################################################

class UserOrganizationMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = UserOrganization.objects.all()
        # kwargs['widget'] = forms.CheckboxSelectMultiple()
        kwargs['widget'] = forms.SelectMultiple(attrs={'data-placeholder':'เลือกกลุ่มผู้ใช้', 'style':'width:500px;'}) # Use for 'Chosen' jQuery plugin
        forms.ModelMultipleChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return obj.user.get_profile().get_fullname()


class OrganizationGroupMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = OrganizationGroup.objects.all()
        kwargs['widget'] = forms.SelectMultiple(attrs={'data-placeholder':'เลือกกลุ่มผู้ใช้', 'style':'width:500px;'}) # Use for 'Chosen' jQuery plugin
        forms.ModelMultipleChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return obj.name


class UserProfileForm(forms.Form):
    first_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))
    last_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))


# ORGANIZATION MANAGEMENT

class InviteOrganizationUserForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'span6'}))
    admin_permissions = forms.ModelMultipleChoiceField(required=False, queryset=OrganizationAdminPermission.objects.all(), widget=forms.CheckboxSelectMultiple())
    groups = OrganizationGroupMultipleChoiceField()

    def __init__(self, organization, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)

        self.organization = organization
        self.fields['groups'].queryset = OrganizationGroup.objects.filter(organization=organization).order_by('name')

    def clean_email(self):
        email = self.cleaned_data.get('email', '')

        if UserOrganizationInvitation.objects.filter(email=email, organization=self.organization).exists():
            raise forms.ValidationError(u'มีการส่งคำขอเพิ่มผู้ใช้ถึงผู้ใช้คนนี้ก่อนหน้านี้แล้ว')

        if UserOrganization.objects.filter(organization=self.organization, user__email=email).exists():
            raise forms.ValidationError(u'ผู้ใช้คนนี้อยู่ใน%s %s แล้ว' % (self.organization.prefix, self.organization.name))

        return email


class UpdateOrganizationUserInviteForm(forms.Form):
    admin_permissions = forms.ModelMultipleChoiceField(required=False, queryset=OrganizationAdminPermission.objects.all(), widget=forms.CheckboxSelectMultiple())
    groups = OrganizationGroupMultipleChoiceField()

    def __init__(self, organization, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)

        self.organization = organization
        self.fields['groups'].queryset = OrganizationGroup.objects.filter(organization=organization).order_by('name')


class ClaimOrganizationUserForm(forms.Form):
    first_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))
    last_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError(_('The two password fields didn\'t match.'))
        return password2


class EditOrganizationUserForm(forms.Form):
    admin_permissions = forms.ModelMultipleChoiceField(required=False, queryset=OrganizationAdminPermission.objects.all(), widget=forms.CheckboxSelectMultiple())
    groups = OrganizationGroupMultipleChoiceField()

    def __init__(self, organization, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)

        self.organization = organization
        self.fields['groups'].queryset = OrganizationGroup.objects.filter(organization=organization).order_by('name')


class OrganizationGroupForm(forms.Form):
    name = StrippedCharField(max_length=100, widget=forms.TextInput(attrs={'class':'span9'}))
    description = StrippedCharField(required=False, max_length=500, widget=forms.Textarea(attrs={'class':'span9', 'rows':'3'}))
    members = UserOrganizationMultipleChoiceField(required=False)

    def __init__(self, organization, *args, **kwargs):
        super(OrganizationGroupForm, self).__init__(*args, **kwargs)
        self.fields['members'].queryset = UserOrganization.objects.filter(organization=organization).order_by('user__userprofile__first_name')


# DOCUMENT #############################################################################################################

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
