from django import forms
from django.utils.translation import ugettext_lazy as _

from common.forms import StrippedCharField

from publisher.forms import GeneralUploadPublicationForm, PublicationCategoryMultipleChoiceField, EditPublicationForm

from publisher.models import Publication
from publisher.magazine.models import Magazine, MagazineIssue

class PublisherMagazineChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['empty_label'] = ''
        kwargs['queryset'] = Magazine.objects.all().order_by('title')
        forms.ModelChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return '%s' % (obj.title)



class UploadPublicationForm(GeneralUploadPublicationForm):
    magazine = PublisherMagazineChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        forms.Form.__init__(self, *args, **kwargs)

        self.fields['magazine'].queryset = Magazine.objects.filter(publisher=self.publisher).order_by('title')
    
    def after_upload(self, request, publication):
        if self.cleaned_data['magazine']:
            magazine_issue = MagazineIssue.objects.create(publication=publication, magazine=self.cleaned_data['magazine'])

class FinishUploadMagazineIssueForm(forms.Form):
    next = forms.CharField(required=False, widget=forms.HiddenInput())
    magazine = PublisherMagazineChoiceField(required=False)
    magazine_name = StrippedCharField(required=False, widget=forms.TextInput(attrs={'class':'span8'}))
    categories = PublicationCategoryMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple())

    title = StrippedCharField(widget=forms.TextInput(attrs={'class':'span8'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))

    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        self.publication = kwargs.pop('publication', None)
        self.to_create_magazine = kwargs.pop('to_create_magazine', None)
        forms.Form.__init__(self, *args, **kwargs)

        self.fields['magazine'].queryset = Magazine.objects.filter(publisher=self.publisher).order_by('title')
    
    def clean_magazine(self):
        magazine = self.cleaned_data['magazine']
        if not self.to_create_magazine and not magazine:
            raise forms.ValidationError(_(u'This field is required.'))
        
        return magazine
    
    def clean_magazine_name(self):
        magazine_name = self.cleaned_data['magazine_name']
        if self.to_create_magazine and not magazine_name:
            raise forms.ValidationError(_(u'This field is required.'))
        
        return magazine_name

class MagazineForm(forms.Form):
    title = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span8'}))
    description = StrippedCharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'3'}))
    categories = PublicationCategoryMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple())

class EditMagazinePublicationForm(EditPublicationForm):
    pass