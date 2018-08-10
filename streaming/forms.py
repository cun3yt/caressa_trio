from streaming.models import AudioFile
from django import forms
from mutagen.mp3 import MP3
from urllib.error import HTTPError
from urllib.request import urlretrieve


class AudioFileForm(forms.ModelForm):
    class Meta:
        model = AudioFile
        exclude = [id, ]

    def clean(self):
        url = self.cleaned_data.get('url')
        try:
            filename, headers = urlretrieve(url)
            audio = MP3(filename)
        except HTTPError:
            raise forms.ValidationError("URL is not publicly accessible. Please make the URL accessible!")

        return self.cleaned_data
