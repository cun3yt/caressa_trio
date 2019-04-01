from streaming.models import AudioFile
from django import forms
from django.forms.widgets import TextInput, Textarea
from mutagen.mp3 import MP3
from urllib.error import HTTPError
from urllib.request import urlretrieve


class MP3AccessibilityCheckMixin:
    @staticmethod
    def validate_accessibility(url):
        try:
            filename, headers = urlretrieve(url)
            audio = MP3(filename)
        except HTTPError:
            raise forms.ValidationError("URL is not publicly accessible. Please make the URL accessible!")


class AudioForm(MP3AccessibilityCheckMixin, forms.ModelForm):
    class Meta:
        model = AudioFile
        exclude = ['id', 'type', ]

        widgets = {
            'name': TextInput(),
            'description': Textarea(attrs={'cols': 40, 'rows': 2})
        }

    def clean(self):
        url = self.cleaned_data.get('url')
        self.validate_accessibility(url)
        return self.cleaned_data
