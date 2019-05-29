from google.cloud.texttospeech import TextToSpeechClient, types, enums
from django.utils.crypto import get_random_string
from datetime import datetime

from utilities.logger import log_warning
from utilities.aws_operations import upload_mp3_to_s3
from .setup import credentials


def _gender_to_enum(gender='neutral'):
    list_of_genders = ['neutral', 'male', 'female', ]
    assert gender in list_of_genders, (
        "gender parameter is supposed to be one of these: {}".format(', '.join(list_of_genders))
    )
    if gender == 'neutral':
        return enums.SsmlVoiceGender.NEUTRAL
    elif gender == 'male':
        return enums.SsmlVoiceGender.MALE
    elif gender == 'female':
        return enums.SsmlVoiceGender.FEMALE
    else:
        log_warning("Gender is not known: {}".format(gender))
        return enums.SsmlVoiceGender.SSML_VOICE_GENDER_UNSPECIFIED


def tts(gender='neutral', **kwargs) -> (str, str):
    text = kwargs.get('text', None)
    ssml = kwargs.get('ssml', None)
    gender_enum = _gender_to_enum(gender)

    if not text and not ssml:
        raise ValueError('either text or ssml must be provided as a keyword argument, you provide nothing')
    elif text and ssml:
        raise ValueError('either text or ssml must be provided as a keyword argument, not both of them')

    client = TextToSpeechClient(credentials=credentials)

    synthesis_input = types.SynthesisInput(**kwargs)

    voice = types.VoiceSelectionParams(language_code='en-US', ssml_gender=gender_enum)
    audio_config = types.AudioConfig(audio_encoding=enums.AudioEncoding.MP3)
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    filename = '{now}-{random}.mp3'.format(now=datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S"),
                                           random=get_random_string(25))
    local_file_path = '/tmp/{filename}'.format(filename=filename)

    with open(local_file_path, 'wb') as out:
        out.write(response.audio_content)

    return filename, local_file_path


def tts_to_s3(return_format: str, **kwargs) -> str:
    filename, local_file_path = tts(**kwargs)
    file_key = 'tts/{filename}'.format(filename=filename)
    return upload_mp3_to_s3(file_key, local_file_path, return_format)
