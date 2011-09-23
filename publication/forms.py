from django import forms

from publication.models import Publisher, Periodical, PublicationCategory

class PublisherPeriodicalChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['empty_label'] = None
        kwargs['queryset'] = Periodical.objects.all().order_by('title')
        forms.ModelChoiceField.__init__(self, *args, **kwargs)

    def label_from_instance(self, obj):
        return '%s' % (obj.title)

class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ('name', 'address', 'telephone', 'website')

class UploadPeriodicalIssueForm(forms.Form):
    def __init__(self, *args, **kwargs):
        publisher = kwargs.pop('publisher', None)
        forms.Form.__init__(self, *args, **kwargs)

        if publisher:
            self.fields["periodical"].queryset = Periodical.objects.filter(publisher=publisher).order_by('title')
            self.publisher = publisher

    publication_uid = forms.CharField(widget=forms.HiddenInput)
    periodical = PublisherPeriodicalChoiceField()
    issue_name = forms.CharField()
    description = forms.CharField(required=False, widget=forms.Textarea)

class UploadBookForm(forms.Form):
    publication_uid = forms.CharField(widget=forms.HiddenInput)
    title = forms.CharField()
    description = forms.CharField(required=False, widget=forms.Textarea)
    author = forms.CharField()
    isbn = forms.CharField(required=False)

    categories = forms.ModelMultipleChoiceField(required=False, queryset=PublicationCategory.objects.all(), widget=forms.CheckboxSelectMultiple())    