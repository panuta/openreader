from django import forms
from django.utils.translation import ugettext_lazy as _

from widgets import YUICalendar, HourOnlyTimeInput

from common.forms import StrippedCharField

from publication.models import Publisher, Periodical, PublicationCategory

class PublisherPeriodicalChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['empty_label'] = ''
        kwargs['queryset'] = Periodical.objects.all().order_by('title')
        forms.ModelChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return '%s' % (obj.title)

# Form classes

class PublisherForm(forms.Form):
    name = StrippedCharField()

class UploadPublicationForm(forms.Form):
    type = forms.CharField(max_length=50, required=False)
    publication = forms.FileField()

class FinishUploadPeriodicalIssueForm(forms.Form):
    periodical = PublisherPeriodicalChoiceField(required=False)
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'span10'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))
    publish_status = forms.ChoiceField(choices=(('unpublished', 'Unpulished'), ('scheduled', 'Scheduled'), ('published', 'Published')))
    schedule_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_schedule_date'}), required=False)
    schedule_time = forms.TimeField(widget=HourOnlyTimeInput(), required=False)

    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        self.uploading_publication = kwargs.pop('uploading_publication', None)
        forms.Form.__init__(self, *args, **kwargs)

        self.fields['periodical'].queryset = Periodical.objects.filter(publisher=self.publisher).order_by('title')
    
    def clean_periodical(self):
        data = self.cleaned_data.get('periodical')
        if not self.uploading_publication.parent_id and not data:
            raise forms.ValidationError(_(u'This field is required.'))
        
        return data
    
    def clean(self):
        cleaned_data = self.cleaned_data
        publish_status = cleaned_data.get('publish_status')
        schedule_date = cleaned_data.get('schedule_date')
        schedule_time = cleaned_data.get('schedule_time')

        if publish_status == 'scheduled' and not (schedule_date or schedule_time):
            self._errors['publish_status'] = self.error_class([_(u'This field is required.')])
        
        return cleaned_data

class FinishUploadPeriodicalIssueForm(forms.Form):
    periodical = PublisherPeriodicalChoiceField(required=False)
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'span10'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))
    publish_status = forms.ChoiceField(choices=(('unpublished', 'Unpulished'), ('scheduled', 'Scheduled'), ('published', 'Published')))
    schedule_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_schedule_date'}), required=False)
    schedule_time = forms.TimeField(widget=HourOnlyTimeInput(), required=False)

    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        self.uploading_publication = kwargs.pop('uploading_publication', None)
        forms.Form.__init__(self, *args, **kwargs)
        
        self.fields['periodical'].queryset = Periodical.objects.filter(publisher=self.publisher).order_by('title')
    
    def clean_periodical(self):
        data = self.cleaned_data.get('periodical')
        if not self.uploading_publication.parent_id and not data:
            raise forms.ValidationError(_(u'This field is required.'))
        
        return data
    
    def clean(self):
        cleaned_data = self.cleaned_data
        publish_status = cleaned_data.get('publish_status')
        schedule_date = cleaned_data.get('schedule_date')
        schedule_time = cleaned_data.get('schedule_time')

        if publish_status == 'scheduled' and not (schedule_date or schedule_time):
            self._errors['publish_status'] = self.error_class([_(u'This field is required.')])
        
        return cleaned_data


"""
    def __init__(self, *args, **kwargs):
        publisher = kwargs.pop('publisher', None)
        forms.Form.__init__(self, *args, **kwargs)

        if publisher:
            self.fields['periodical'].queryset = Periodical.objects.filter(publisher=publisher).order_by('title')
            self.publisher = publisher
"""

"""
    def clean(self):
        cleaned_data = self.cleaned_data
        periodical_title = cleaned_data.get('periodical_title')
        periodical = cleaned_data.get('periodical')

        if not periodical_title and not periodical:
            raise forms.ValidationError('Choose a periodical or create a new periodical')
        
        return cleaned_data
"""

class FinishUploadBookForm(forms.Form):
    title = forms.CharField()
    description = forms.CharField(required=False, widget=forms.Textarea)
    author = forms.CharField()
    isbn = forms.CharField(required=False)

    categories = forms.ModelMultipleChoiceField(required=False, queryset=PublicationCategory.objects.all(), widget=forms.CheckboxSelectMultiple())    

# Publisher Periodicals

class PublisherPeriodicalForm(forms.Form):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'span9', 'rows':'3'}))

    # categories = models.ManyToManyField('PublicationCategory', related_name='periodical_categories')

# Publisher Management

class PublisherProfileForm(forms.Form):
    name = forms.CharField(max_length=200)

class PublisherShelfForm(forms.Form):
    name = StrippedCharField(max_length=200, widget=forms.TextInput(attrs={'class':'span9'}))
    description = StrippedCharField(widget=forms.Textarea(attrs={'class':'span9', 'rows':'3'}))

# class FinishUploadPictureForm(forms.Form):
#     title = forms.CharField()
#     description = forms.CharField(required=False, widget=forms.Textarea)