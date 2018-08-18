from streaming.models import AudioFile
from utilities.logger import log
from urllib.request import urlretrieve
from mutagen.mp3 import MP3, HeaderNotFoundError
from urllib.error import HTTPError


def audio_file_accessibility_and_duration(instance):
    try:
        filename, headers = urlretrieve(instance.url)
        audio = MP3(filename)
        instance.duration = round(audio.info.length)
        instance.save()
        log('Content Is Public')
        log('Duration of {name} : {duration}'.format(name=instance.name, duration=round(audio.info.length)))
    except HTTPError:
        instance.duration = -1
        log('HTTP Error!')
        instance.save()


def run():
    log('~~~ SCRIPT STARTS ~~~')

    duration_zero = AudioFile.objects.all().filter(duration='0')

    for instance in duration_zero:
        try:
            audio_file_accessibility_and_duration(instance=instance)
        except HeaderNotFoundError:
            pass
    log('~~~ SCRIPT FINISHED ~~~')
