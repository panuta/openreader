# -*- encoding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from widgets import YUICalendar, HourMinuteTimeInput

from common.forms import StrippedCharField
from common.permissions import ROLE_CHOICES

from accounts.models import Role
from publisher.models import Publisher, PublicationCategory, Module, PublisherShelf

class PublicationStatusField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = (('unpublish', 'ยังไม่เผยแพร่'), ('schedule', 'ตั้งเวลาเผยแพร่'), ('publish', 'เผยแพร่'))
        forms.ChoiceField.__init__(self, *args, **kwargs)

class PublicationCategoryMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = PublicationCategory.objects.all().order_by('name')
        forms.ModelMultipleChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return '%s' % (obj.name)

class ModuleMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = Module.objects.all().order_by('module_type', 'title')
        forms.ModelMultipleChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return '%s - %s' % (obj.module_type, obj.title)

class PublisherShelfMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = PublisherShelf.objects.all().order_by('name')
        forms.ModelMultipleChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return '%s' % (obj.name)

# Form classes

class PublisherForm(forms.Form):
    name = StrippedCharField()

class GeneralUploadPublicationForm(forms.Form):
    module = forms.CharField(widget=forms.HiddenInput(), max_length=50)
    publication = forms.FileField()

    def clean(self):
        cleaned_data = self.cleaned_data
        # TODO: Check eligible file type from all available modules
        return cleaned_data
    
    def valid_file_type(self):
        return False
    
    def after_upload(self, request, publication):
        pass

# Publication

class EditPublicationForm(forms.Form):
    title = StrippedCharField(widget=forms.TextInput(attrs={'class':'span8'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))
    from_page = forms.CharField(required=False, widget=forms.HiddenInput())

class EditPublicationStatusForm(forms.Form):
    status = PublicationStatusField()
    schedule_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_schedule_date'}), required=False)
    schedule_time = forms.TimeField(widget=HourMinuteTimeInput(), required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        status = cleaned_data.get('status')
        schedule_date = cleaned_data.get('schedule_date')
        schedule_time = cleaned_data.get('schedule_time')

        if status == 'schedule' and not schedule_date:
            self._errors['schedule_date'] = self.error_class([_(u'This field is required.')])
        
        if status == 'schedule' and not schedule_time:
            self._errors['schedule_time'] = self.error_class([_(u'This field is required.')])
        
        return cleaned_data

# Publisher Management

class PublisherProfileForm(forms.Form):
    name = StrippedCharField(max_length=200)

class PublisherShelfForm(forms.Form):
    name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span9', 'rows':'3'}))

class InvitePublisherUserForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'span6'}))
    role = forms.ModelChoiceField(queryset=Role.objects.all(), empty_label='')

class ClaimPublisherUserForm(forms.Form):
    first_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))
    last_name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

class EditPublisherUserForm(forms.Form):
    role = forms.ModelChoiceField(queryset=Role.objects.all(), empty_label=None)

# class FinishUploadPictureForm(forms.Form):
#     title = forms.CharField()
#     description = forms.CharField(required=False, widget=forms.Textarea)