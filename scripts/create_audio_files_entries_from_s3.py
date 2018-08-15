from boto.s3.connection import S3Connection
from urllib.parse import quote_plus
from streaming.models import AudioFile
from utilities.logger import log
import os.path
from caressa.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, MEDIA_BUCKET


def is_file_importable(filename, public_url):
    proper_audio_extensions = ('.ra', '.aif', '.aiff', '.aifc', '.wav', '.au', '.snd', '.mp3', '.mp2')
    return filename.endswith(proper_audio_extensions) \
        and (AudioFile.objects.all().filter(url=public_url).count() == 0)


def run():
    conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(MEDIA_BUCKET)

    log('~~~ SCRIPT STARTS ~~~')

    audio_files_batch = []
    for key in bucket.list():
        s3_audio_file_split = key.name.split('/')
        url = '{}/{}/{}'.format('https://s3-us-west-1.amazonaws.com', MEDIA_BUCKET, quote_plus(key.name, '/'))

        if not is_file_importable(key.name, url):
            log('URL exist or not a proper audio file.')
            continue

        name = os.path.splitext(s3_audio_file_split[-1])[0]
        audio_type = 'song'
        description = '/'.join(key.name.split('/')[:-1])

        log('~~~~~~~~~~~~~~~~~~~~')
        log('Audio Type : {}'.format(audio_type))
        log('Url : {}'.format(url))
        log('Name : {}'.format(name))
        log('Description: {}'.format(description))

        new_audio_from_s3 = AudioFile(audio_type=audio_type, url=url, name=name, description=description)
        audio_files_batch.append(new_audio_from_s3)

        log('Appended')
        log('~~~~~~~~~~~~~~~~~~~~')

    AudioFile.objects.bulk_create(audio_files_batch, 1000)
    log('~~~ SCRIPT FINISHED ~~~')
