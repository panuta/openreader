from django import forms

from publication.models import Publisher

class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ('name', 'address', 'telephone', 'website')

