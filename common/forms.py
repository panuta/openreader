from django import forms

class StrippedCharField(forms.CharField):
    def __init__(self, max_length=None, min_length=None, strip=True, *args, **kwargs):
        super(StrippedCharField, self).__init__(max_length, min_length, *args, **kwargs)
        self.strip = strip

    def clean(self, value):
        if value:
            value = value.strip()
        return super(StrippedCharField, self).clean(value)