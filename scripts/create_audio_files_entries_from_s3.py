from boto.s3.connection import S3Connection
from urllib.parse import quote_plus
from streaming.models import AudioFile
import os.path
from caressa.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, MEDIA_BUCKET


def run():

    conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(MEDIA_BUCKET)
    audio_extensions = ('.ra', '.aif', '.aiff', '.aifc', '.wav', '.au', '.snd', '.mp3', '.mp2')

    for key in bucket.list():
        s3_audio_file_split = key.name.split('/')
        audio_name = os.path.splitext(s3_audio_file_split[-1])[0]

        if key.name.endswith(audio_extensions) and AudioFile.objects.all().filter(name=audio_name).count() == 0:
            audio_type = s3_audio_file_split[0]
            url = '{}/{}/{}'.format('https://s3-us-west-1.amazonaws.com', MEDIA_BUCKET, quote_plus(key.name, '/'))
            description = '/'.join(key.name.split('/')[:-1])

            new_audio_from_s3 = AudioFile(audio_type=audio_type, url=url, name=audio_name, description=description)
            new_audio_from_s3.save()
