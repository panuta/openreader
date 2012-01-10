# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

from common.forms import StrippedCharField
from common.permissions import ROLE_CHOICES

from accounts.models import OrganizationRole, UserOrganizationInvitation, UserOrganization

class EmailAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    email/password logins.
    """
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_('Please enter a correct username and password. Note that both fields are case-sensitive.'))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_('This account is inactive.'))
        self.check_for_test_cookie()
        return self.cleaned_data

    def check_for_test_cookie(self):
        if self.request and not self.request.session.test_cookie_worked():
            raise forms.ValidationError(
                _('Your Web browser doesn\'t appear to have cookies enabled. '
                  'Cookies are required for logging in.'))

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache

class UserProfileForm(forms.Form):
    first_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))
    last_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))

# ORGANIZATION MANAGEMENT

class OrganizationProfileForm(forms.Form):
    name = StrippedCharField(max_length=200)

class OrganizationShelfForm(forms.Form):
    name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span9', 'rows':'3'}))

class InviteOrganizationUserForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'span6'}))
    role = forms.ModelChoiceField(queryset=OrganizationRole.objects.all(), empty_label='')

    def __init__(self, organization, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)

        self.organization = organization
        self.fields['role'].queryset = OrganizationRole.objects.filter(organization=organization).order_by('name')

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        
        if UserOrganizationInvitation.objects.filter(user_email=email, organization=self.organization).exists():
            raise forms.ValidationError(u'มีการส่งคำขอเพิ่มผู้ใช้ถึงผู้ใช้คนนี้ก่อนหน้านี้แล้ว')
        
        if UserOrganization.objects.filter(organization=self.organization, user__email=email).exists():
            raise forms.ValidationError(u'ผู้ใช้คนนี้อยู่ใน%s %s แล้ว' % (self.organization.prefix, self.organization.name))
        
        return email

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
    role = forms.ModelChoiceField(queryset=OrganizationRole.objects.all(), empty_label=None)

    def __init__(self, organization, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.fields['role'].queryset = OrganizationRole.objects.filter(organization=organization).order_by('name')

class OrganizationRoleForm(forms.Form):
    name = StrippedCharField(max_length=100, widget=forms.TextInput(attrs={'class':'span9'}))
    description = StrippedCharField(required=False, max_length=500, widget=forms.Textarea(attrs={'class':'span9', 'rows':'3'}))
    is_admin = forms.BooleanField(required=False)

class RemoveOrganizationRoleForm(forms.Form):
    role = forms.ModelChoiceField(required=False, queryset=OrganizationRole.objects.all(), empty_label='')

    def __init__(self, organization, role, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.role = role
        self.fields['role'].queryset = OrganizationRole.objects.filter(organization=organization).exclude(id=role.id).order_by('name')
    
    def clean_role(self):
        new_role = self.cleaned_data.get('role', '')

        if not new_role and UserOrganization.objects.filter(role=self.role).count():
            raise forms.ValidationError(_('This field is required.'))
        
        return new_role
