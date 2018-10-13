from google.cloud.texttospeech import TextToSpeechClient, types, enums
from boto3 import client as boto3_client
from django.utils.crypto import get_random_string
from datetime import datetime

S3_REGION = 'https://s3-us-west-1.amazonaws.com'
S3_PRODUCTION_BUCKET = 'caressa-prod'


def tts(**kwargs) -> (str, str):
    text = kwargs.get('text', None)
    ssml = kwargs.get('ssml', None)

    if not text and not ssml:
        raise ValueError('either text or ssml must be provided as a keyword argument, you provide nothing')
    elif text and ssml:
        raise ValueError('either text or ssml must be provided as a keyword argument, not both of them')

    client = TextToSpeechClient()

    synthesis_input = types.SynthesisInput(**kwargs)

    voice = types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=enums.SsmlVoiceGender.NEUTRAL)

    audio_config = types.AudioConfig(audio_encoding=enums.AudioEncoding.MP3)

    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    filename = '{now}-{random}.mp3'.format(now=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S"),
                                           random=get_random_string(25))
    local_file_path = '/tmp/{filename}'.format(filename=filename)

    with open(local_file_path, 'wb') as out:
        out.write(response.audio_content)

    return filename, local_file_path


def tts_to_s3(**kwargs) -> str:
    filename, local_file_path = tts(**kwargs)
    file_key = 'tts/{filename}'.format(filename=filename)
    s3_client = boto3_client('s3')
    s3_client.upload_file(local_file_path,
                          S3_PRODUCTION_BUCKET,
                          file_key,
                          ExtraArgs={'ACL': 'public-read', 'ContentType': 'audio/mp3'})

    url = '{region}/{bucket}/{file_key}'.format(region=S3_REGION,
                                                bucket=S3_PRODUCTION_BUCKET,
                                                file_key=file_key)
    return url
