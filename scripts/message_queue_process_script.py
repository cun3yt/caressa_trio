from streaming.models import Messages, AudioFile, Tag
from alexa.models import User
from caressa.settings import S3_RAW_UPLOAD_BUCKET, S3_REGION, S3_PRODUCTION_BUCKET
import boto3

from utilities.aws_operations import move_file_from_upload_to_prod_bucket
from utilities.logger import log, log_error
from pydub import AudioSegment
from utilities.statistics import check_event_uniform_distribution
from utilities.real_time_communication import send_instance_message
from voice_service.google import tts
from time import sleep
import traceback


# todo revisit `senior_communication_channel` part, it may need to be `facility_channel` in some cases


def _encode_audio_from_aws_and_upload_to_prod_bucket(ios_file_key):
    s3 = boto3.resource('s3')
    file_key = ios_file_key + '.mp3'
    s3.Bucket(S3_RAW_UPLOAD_BUCKET).download_file(ios_file_key, '/tmp/{}'.format(ios_file_key))
    webm_audio = AudioSegment.from_file('/tmp/{}'.format(ios_file_key))
    webm_audio.export('/tmp/{}'.format(file_key), format='mp3')
    s3_client = boto3.client('s3')
    s3_client.upload_file('/tmp/{}'.format(file_key),
                          S3_PRODUCTION_BUCKET,
                          '{file_key}'.format(file_key=file_key),
                          ExtraArgs={'ACL': 'public-read', 'ContentType': 'audio/mp3'})
    return file_key


def audio_worker(publisher, next_queued_job: Messages):
    next_queued_job.process_state = Messages.PROCESS_RUNNING
    next_queued_job.save()

    log('Queue State : {process_state}'.format(process_state=next_queued_job.process_state))

    mail_type = 'voice_mail'
    if publisher == 'facility':
        mail_type = 'urgent_mail'

    ios_file_key = next_queued_job.message['key']

    if not ios_file_key.endswith('.mp3'):
        file_key = _encode_audio_from_aws_and_upload_to_prod_bucket(ios_file_key)
    else:
        file_key = ios_file_key
        move_file_from_upload_to_prod_bucket(ios_file_key, ios_file_key)

    audio_type = '{publisher}_voice_record'.format(publisher=publisher)
    description = 'Audio Record from {publisher}'.format(publisher=publisher)
    url = '{region}/{bucket}/{file_key}'.format(region=S3_REGION,
                                                bucket=S3_PRODUCTION_BUCKET,
                                                file_key=file_key)

    new_audio = AudioFile(audio_type=audio_type, url=url, name=file_key, description=description)
    new_audio.save()

    tag, _ = Tag.objects.get_or_create(name='{publisher}-update'.format(publisher=publisher))
    new_audio.tags.add(tag)

    next_queued_job.process_state = Messages.PROCESS_COMPLETE
    log(next_queued_job.process_state)
    next_queued_job.save()

    user_id = next_queued_job.message.get('user')
    assert user_id is not None, "User ID supposed to be in the message as `user` field in JSON `message`"
    source = User.objects.get(pk=user_id)

    if source.is_provider():
        channels = source.communication_channels()
        assert len(channels) == 1, "Provider is supposed to have only one channel, which is a SLF channel"
        send_instance_message(channels[0], mail_type, {'url': url, 'hash': new_audio.hash})
    else:
        assert source.is_family(), (
            "Source must be family if not a provider since senior cannot trigger a message (at the moment)"
        )
        destination = source.circle_set.all()[0].person_of_interest
        send_instance_message(destination.senior_communication_channel, mail_type, {'url': url, 'hash': new_audio.hash})

    return 'Job Finished...'


def text_worker(publisher, next_queued_job: Messages):
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

    user_id = next_queued_job.message.get('user')
    assert user_id is not None, "User ID supposed to be in the message as `user` field in JSON `message`"
    source = User.objects.get(pk=user_id)

    destination = source.circle_set.all()[0].person_of_interest     # todo from the senior living community part ???
    send_instance_message(destination.senior_communication_channel, mail_type, {'url': url, 'hash': new_audio.hash})

    return 'Job Finished...'


def personalization_worker(publisher, next_queued_job: Messages):
    user_id = next_queued_job.message.get('user')
    if user_id:
        user = User.objects.get(id=user_id)
        text = 'Your music preferences updated by {first_name}'.format(first_name=user.first_name)
    else:
        text = 'Your family updated your music preferences'

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

    user_id = next_queued_job.message.get('user')
    assert user_id is not None, "User ID supposed to be in the message as `user` field in JSON `message`"
    source = User.objects.get(pk=user_id)

    destination = source.circle_set.all()[0].person_of_interest

    send_instance_message(destination.senior_communication_channel, mail_type, {'url': url, 'hash': new_audio.hash})

    log('Job Finished...')


worker_registry = {     # Mapping from message type to [consumer (worker fn), publisher (originator)] pair
    'family_ios_audio': {
        'publisher': 'family',
        'consumer': 'audio_worker',
    },
    'family_ios_text': {
        'publisher': 'family',
        'consumer': 'text_worker',
    },
    'facility_ios_audio': {
        'publisher': 'facility',
        'consumer': 'audio_worker',
    },
    'facility_web_audio': {
        'publisher': 'facility',
        'consumer': 'audio_worker',
    },
    'facility_ios_text': {
        'publisher': 'facility',
        'consumer': 'text_worker',
    },
    'genres': {
        'publisher': 'family',
        'consumer': 'personalization_worker',
    },
}


# todo: Fix: successful re-run of failed messages still contain the error messages
def run():
    while True:
        messages_qs = Messages.objects.filter(process_state=Messages.PROCESS_QUEUED).order_by('created')
        messages_count = messages_qs.count()

        if messages_count == 0:
            if check_event_uniform_distribution(0.05):
                log('Queue is empty, waiting for 2 seconds...')
            sleep(2)
            continue

        next_queued_job = messages_qs[0]
        log('Processing 1 of {num} Queued Message, id: {id}'.format(num=messages_count, id=next_queued_job))

        try:
            message = next_queued_job.message
            typ = message['message_type']
            consumer = worker_registry[typ]['consumer']
            publisher = worker_registry[typ]['publisher']
            globals()[consumer](publisher, next_queued_job)
        except Exception:
            error_message = traceback.format_exc()
            log_error(error_message)
            next_queued_job.message['error'] = error_message
            next_queued_job.process_state = Messages.PROCESS_FAILED
            next_queued_job.save()
            continue
