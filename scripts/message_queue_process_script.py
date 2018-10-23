from streaming.models import Messages, AudioFile, Tag, VoiceMessageStatus
from alexa.models import User
from caressa.settings import S3_RAW_UPLOAD_BUCKET, S3_REGION, S3_PRODUCTION_BUCKET
import boto3
from utilities.logger import log
from pydub import AudioSegment
from caressa.settings import pusher_client
from voice_service.google import tts
from time import sleep
import traceback

pusher_channel = 'family.senior.1'    # todo move to `hard-coding`


def audio_worker(publisher, next_queued_job):
    ios_file_key = next_queued_job.message['key']
    file_key = ios_file_key + '.mp3'
    mail_type = 'voice_mail'
    if publisher == 'facility':
        mail_type = 'urgent_mail'

    next_queued_job.process_state = Messages.PROCESS_RUNNING
    next_queued_job.save()
    log('Queue State : {process_state}'.format(process_state=next_queued_job.process_state))

    s3 = boto3.resource('s3')
    s3.Bucket(S3_RAW_UPLOAD_BUCKET).download_file(ios_file_key, '/tmp/{}'.format(ios_file_key))
    webm_audio = AudioSegment.from_file('/tmp/{}'.format(ios_file_key), format='wav')
    webm_audio.export('/tmp/{}'.format(file_key), format='mp3')
    s3_client = boto3.client('s3')
    s3_client.upload_file('/tmp/{}'.format(file_key),
                          S3_PRODUCTION_BUCKET,
                          '{file_key}'.format(file_key=file_key),
                          ExtraArgs={'ACL': 'public-read', 'ContentType': 'audio/mp3'})

    audio_type = '{publisher}_voice_record'.format(publisher=publisher)
    description = 'Audio Record from {publisher}'.format(publisher=publisher)
    url = '{region}/{bucket}/{file_key}'.format(region=S3_REGION,
                                                bucket=S3_PRODUCTION_BUCKET,
                                                file_key=file_key)

    new_audio = AudioFile(audio_type=audio_type, url=url, name=file_key, description=description)
    new_audio.save()

    tag = Tag.objects.get(name='{publisher}-update'.format(publisher=publisher))
    new_audio.tags.add(tag)

    next_queued_job.process_state = Messages.PROCESS_COMPLETE
    log(next_queued_job.process_state)
    next_queued_job.save()

    pusher_client.trigger(pusher_channel,
                          mail_type,
                          url)

    source = User.objects.get(pk=2)    # todo move to `hard-coding`
    destination = User.objects.get(pk=1)    # todo move to `hard-coding`
    new_voice_message_status = VoiceMessageStatus(source=source, destination=destination, key=file_key)
    new_voice_message_status.save()

    return 'Job Finished...'


def text_worker(publisher, next_queued_job):
    text = next_queued_job.message['content']
    mail_type = 'voice_mail'
    if publisher == 'facility':
        mail_type = 'urgent_mail'

    next_queued_job.process_state = Messages.PROCESS_RUNNING
    next_queued_job.save()
    log('Queue State : {process_state}'.format(process_state=next_queued_job.process_state))

    file_key = tts.tts_to_s3(text=text, return_format='key')

    audio_type = '{publisher}_text_message'.format(publisher=publisher)
    description = 'Audio Record from {publisher}'.format(publisher=publisher)
    url = '{region}/{bucket}/{file_key}'.format(region=S3_REGION,
                                                bucket=S3_PRODUCTION_BUCKET,
                                                file_key=file_key)

    new_audio = AudioFile(audio_type=audio_type, url=url, name=file_key, description=description)
    new_audio.save()

    next_queued_job.process_state = Messages.PROCESS_COMPLETE
    log(next_queued_job.process_state)
    log(file_key)
    next_queued_job.save()

    pusher_client.trigger(pusher_channel,
                          mail_type,
                          url)

    source = User.objects.get(pk=2)    # todo move to `hard-coding`
    destination = User.objects.get(pk=1)    # todo move to `hard-coding`
    new_voice_message_status = VoiceMessageStatus(source=source, destination=destination, key=file_key)
    new_voice_message_status.save()

    return 'Job Finished...'


def personalization_worker(publisher, next_queued_job):
    text = 'Your music preferences updated by John'  # todo move to `hard-coding`
    mail_type = 'voice_mail'

    next_queued_job.process_state = Messages.PROCESS_RUNNING
    next_queued_job.save()
    log('Queue State : {process_state}'.format(process_state=next_queued_job.process_state))

    file_key = tts.tts_to_s3(text=text, return_format='key')

    audio_type = '{publisher}_text_message'.format(publisher=publisher)
    description = 'Audio Record from {publisher}'.format(publisher=publisher)
    url = '{region}/{bucket}/{file_key}'.format(region=S3_REGION,
                                                bucket=S3_PRODUCTION_BUCKET,
                                                file_key=file_key)

    new_audio = AudioFile(audio_type=audio_type, url=url, name=file_key, description=description)
    new_audio.save()

    next_queued_job.process_state = Messages.PROCESS_COMPLETE
    log(next_queued_job.process_state)
    log(file_key)
    next_queued_job.save()

    pusher_client.trigger(pusher_channel,
                          mail_type,
                          url)

    source = User.objects.get(pk=2)
    destination = User.objects.get(pk=1)
    new_voice_message_status = VoiceMessageStatus(source=source, destination=destination, key=file_key)
    new_voice_message_status.save()

    log('Job Finished...')


def run():
    while True:
        sleep(2)

        if not Messages.objects.filter(process_state='queued').count() > 0:
            log('Queue is empty...')
            continue

        next_queued_job = Messages.objects.filter(process_state='queued').order_by('created')[0]
        message = next_queued_job.message

        log('Queue State : {process_state}'.format(process_state=next_queued_job.process_state))

        try:
            if message['message_type'] == 'family_ios_audio':
                audio_worker(publisher='family', next_queued_job=next_queued_job)

            elif message['message_type'] == 'family_ios_text':
                text_worker(publisher='family', next_queued_job=next_queued_job)

            elif message['message_type'] == 'facility_ios_audio':
                audio_worker(publisher='facility', next_queued_job=next_queued_job)

            elif message['message_type'] == 'facility_ios_text':
                text_worker(publisher='facility', next_queued_job=next_queued_job)

            elif message['message_type'] == 'genres':
                personalization_worker(publisher='family', next_queued_job=next_queued_job)
        except Exception:
            error_message = traceback.format_exc()
            next_queued_job.message['error'] = error_message
            next_queued_job.process_state = Messages.PROCESS_FAILED
            next_queued_job.save()
            continue
