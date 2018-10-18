from streaming.models import Messages, AudioFile, Tag, VoiceMessageStatus
from alexa.models import User
from caressa.settings import S3_RAW_UPLOAD_BUCKET, S3_REGION, S3_PRODUCTION_BUCKET
import boto3
from utilities.logger import log
from pydub import AudioSegment
from caressa.settings import pusher_client

def run():
    if not Messages.objects.filter(process_state='queued').count() > 0:
        log('Queue is empty...')
        return 'Queue is empty...'

    next_queued_job = Messages.objects.filter(process_state='queued')[0]

    log('Queue State : {process_state}'.format(process_state=next_queued_job.process_state))
    message = next_queued_job.message

    file_key = message['key']

    if message['message_type'] == 'ios-audio':

        next_queued_job.process_state = Messages.PROCESS_RUNNING
        next_queued_job.save()
        log('Queue State : {process_state}'.format(process_state=next_queued_job.process_state))

        s3 = boto3.resource('s3')
        s3.Bucket(S3_RAW_UPLOAD_BUCKET).download_file(file_key, '/tmp/{}'.format(file_key))
        webm_audio = AudioSegment.from_file('/tmp/{}'.format(file_key), format='wav')
        webm_audio.export('/tmp/{}.mp3'.format(file_key), format='mp3')
        s3_client = boto3.client('s3')
        s3_client.upload_file('/tmp/{}.mp3'.format(file_key),
                              S3_PRODUCTION_BUCKET,
                              '{file_key}.mp3'.format(file_key=file_key),
                              ExtraArgs={'ACL': 'public-read', 'ContentType': 'audio/mp3'})

        audio_type = 'family_update'
        publisher = 'Senior\'s Relative'
        description = 'Audio Record from {publisher}'.format(publisher=publisher)
        url = '{region}/{bucket}/{file_key}.mp3'.format(region=S3_REGION,
                                                        bucket=S3_PRODUCTION_BUCKET,
                                                        file_key=file_key)

        new_audio = AudioFile(audio_type=audio_type, url=url, name=file_key, description=description)
        new_audio.save()

        tag = Tag.objects.get(name='family-update')
        new_audio.tags.add(tag)

        next_queued_job.process_state = Messages.PROCESS_COMPLETE
        log(next_queued_job.process_state)
        next_queued_job.save()

        pusher_client.trigger('family.senior.1',
                              'urgent_mail',
                              url)

        source = User.objects.get(pk=2)
        destination = User.objects.get(pk=1)
        new_voice_message_status = VoiceMessageStatus(source=source, destination=destination, key=file_key)
        new_voice_message_status.save()

        return 'Job Finished...'
