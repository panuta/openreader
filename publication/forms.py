from django import forms

from publication.models import Publisher, Periodical, PublicationCategory

class PublisherPeriodicalChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['empty_label'] = None
        kwargs['queryset'] = Periodical.objects.all().order_by('title')
        forms.ModelChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return '%s' % (obj.title)

class PublisherForm(forms.Form):
    name = forms.CharField()

class UploadPublicationForm(forms.Form):
    publication = forms.FileField()

class FinishUploadPeriodicalIssueForm(forms.Form):
    def __init__(self, *args, **kwargs):
        publisher = kwargs.pop('publisher', None)
        forms.Form.__init__(self, *args, **kwargs)

        if publisher:
            self.fields['periodical'].queryset = Periodical.objects.filter(publisher=publisher).order_by('title')
            self.publisher = publisher
    
    periodical_title = forms.CharField(required=False)
    periodical = PublisherPeriodicalChoiceField(required=False)
    title = forms.CharField()
    description = forms.CharField(required=False, widget=forms.Textarea)

    def clean(self):
        cleaned_data = self.cleaned_data
        periodical_title = cleaned_data.get('periodical_title')
        periodical = cleaned_data.get('periodical')

        if not periodical_title and not periodical:
            raise forms.ValidationError('Choose a periodical or create a new periodical')
        
        return cleaned_data

class FinishUploadBookForm(forms.Form):
    title = forms.CharField()
    description = forms.CharField(required=False, widget=forms.Textarea)
    author = forms.CharField()
    isbn = forms.CharField(required=False)

    categories = forms.ModelMultipleChoiceField(required=False, queryset=PublicationCategory.objects.all(), widget=forms.CheckboxSelectMultiple())    


# class FinishUploadPictureForm(forms.Form):
#     title = forms.CharField()
#     description = forms.CharField(required=False, widget=forms.Textarea)