from django import forms

from widgets import YUICalendar, HourOnlyTimeInput

from publication.forms import GeneralUploadPublicationForm

class UploadPublicationForm(GeneralUploadPublicationForm):
    pass

class FinishUploadMagazineIssueForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'span10'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'span10', 'rows':'5'}))
    publish_status = forms.ChoiceField(choices=(('unpublished', 'Unpulished'), ('scheduled', 'Scheduled'), ('published', 'Published')))
    schedule_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_schedule_date'}), required=False)
    schedule_time = forms.TimeField(widget=HourOnlyTimeInput(), required=False)

    # categories = forms.ModelMultipleChoiceField(required=False, queryset=PublicationCategory.objects.all(), widget=forms.CheckboxSelectMultiple())    

    def __init__(self, *args, **kwargs):
        self.publisher = kwargs.pop('publisher', None)
        self.uploading_publication = kwargs.pop('uploading_publication', None)
        forms.Form.__init__(self, *args, **kwargs)

        self.fields['magazine'].queryset = Magazine.objects.filter(publisher=self.publisher).order_by('title')
    
    def clean_magazine(self):
        data = self.cleaned_data.get('magazine')
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