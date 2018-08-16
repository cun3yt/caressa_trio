from django.views.decorators.csrf import csrf_exempt
import json
from utilities.dictionaries import deep_get
from utilities.logger import log
from alexa.models import AUser, User, Session
from datetime import datetime
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from streaming.models import PlaylistHasAudio, UserPlaylistStatus
from django.db import transaction
from botanalytics.amazon import AmazonAlexa
from caressa.settings import botanalytics_api_token


botanalytics = AmazonAlexa(debug=False,
                           token=botanalytics_api_token)


def _create_test_user():
    username = 'Test{date}'.format(date=datetime.now().strftime('%Y%m%d%H%M'))
    test_user = User(username=username,
                     password=get_random_string(),
                     first_name='AnonymousFirstName',
                     last_name='AnonymousLastName',
                     is_staff=False,
                     is_superuser=False,
                     email='test@caressa.ai',
                     phone_number='+14153477898',
                     profile_pic='default_profile_pic', )
    return test_user


@csrf_exempt
def stream_io_wrapper(request):
    request_body = json.loads(request.body)
    response_body = stream_io(request_body)   # type: dict
    # botanalytics.log(request_body, response_body)
    return JsonResponse(response_body)


def stream_io(req_body):
    log(req_body)

    session_id = deep_get(req_body, 'session.sessionId', '')
    user_id = deep_get(req_body, 'context.System.user.userId', '')
    device_id = deep_get(req_body, 'context.System.device.deviceId', '')

    req_type = deep_get(req_body, 'request.type')
    intent = deep_get(req_body, 'request.intent')
    intent_name = deep_get(req_body, 'request.intent.name')

    log("Request Body: {}".format(req_body))
    log("Type: {}".format(req_type))
    log("Intent: {}".format(intent))
    log("Intent Name: {}".format(intent_name))

    alexa_user, is_created = AUser.objects.get_or_create(alexa_device_id=device_id, alexa_user_id=user_id)

    if is_created:
        test_user = _create_test_user()
        test_user.save()
        alexa_user.user = test_user
        alexa_user.save()

    if req_type == 'SessionEndedRequest':
        return stop_session()

    sess, is_new_session = Session.objects.get_or_create(alexa_id=session_id,
                                                         alexa_user=alexa_user)

    if req_type in ['LaunchRequest', ] or intent_name in ['AMAZON.ResumeIntent', ]:
        return resume_session(alexa_user)
    elif intent_name in ['AMAZON.NextIntent', ]:
        return next_intent_response(alexa_user)
    elif req_type in ['AudioPlayer.PlaybackNearlyFinished', ]:
        return enqueue_next_song(alexa_user)
    elif req_type in ['AudioPlayer.PlaybackStarted', ]:
        save_state(alexa_user, req_body)
        return filler()
    elif intent_name in ['AMAZON.PauseIntent', ]:
        return pause_session(alexa_user)
    elif intent is not None:
        return stop_session()

    return filler()


def filler():
    data = {
        "version": "1.0",
        "response": {
            "shouldEndSession": True
        }
    }

    log(" >> LOG: FILLER")

    return data


@transaction.atomic()
def save_state(alexa_user: AUser, req_body):
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(alexa_user.user)
    offset = deep_get(req_body, 'context.AudioPlayer.offsetInMilliseconds')
    token = deep_get(req_body, 'context.AudioPlayer.token')     # this is AudioFile instance's ID

    qs_playlist_entry = status.playlist_has_audio.playlist.playlisthasaudio_set.filter(
        audio_id__exact=token, order_id__gte=status.playlist_has_audio.order_id
    )

    new_playlist_has_audio = None
    if qs_playlist_entry.count() < 1:   # if the currently playing song is not available in the playlist
        new_playlist_has_audio = status.playlist_has_audio.playlist.playlisthasaudio_set.all()[0]
    else:
        new_playlist_has_audio = qs_playlist_entry[0]

    # token (i.e. audio-id) + user-status => which p.h.a?

    status.playlist_has_audio = new_playlist_has_audio
    status.offset = offset
    status.save()

    log(' >> LOG SAVE_STATE: pha: {}, audio: {}, order: {}'.format(
        status.playlist_has_audio.id,
        status.playlist_has_audio.audio.id,
        status.playlist_has_audio.order_id))


@transaction.atomic()
def save_state_by_playlist_entry(alexa_user: AUser, pha: PlaylistHasAudio):
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(alexa_user.user)
    status.playlist_has_audio = pha
    status.offset = 0
    status.save()

    log(' >> LOG: SAVE_STATE_BY_PLAYLIST_ENTRY: pha: {}, audio: {}, order: {}'.format(
        status.playlist_has_audio.id,
        status.playlist_has_audio.audio.id,
        status.playlist_has_audio.order_id))


@transaction.atomic()
def pause_session(alexa_user: AUser):
    log(' >> LOG: PAUSE')
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(alexa_user.user)
    playlist_has_audio = status.playlist_has_audio.next()
    save_state_by_playlist_entry(alexa_user, playlist_has_audio)
    return stop_session()


@transaction.atomic()
def resume_session(alexa_user: AUser):
    log(' >> LOG: RESUME_SESSION')
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(alexa_user.user)  # type: UserPlaylistStatus
    return start_session(status.playlist_has_audio, status.offset)


def stop_session():
    data = {
        "version": "1.0",
        "response": {
            "shouldEndSession": True,
            "directives": [
                {
                    "type": "AudioPlayer.Stop"
                }
            ]
        }
    }

    log(" >> LOG: STOP")

    return data


def start_session(playlist_has_audio: PlaylistHasAudio, offset=0):
    file = playlist_has_audio.audio
    token = file.id

    data = {
        "version": "1.0",
        "response": {
            "shouldEndSession": True,
            "directives": [
                {
                    "type": "AudioPlayer.Play",
                    "playBehavior": "REPLACE_ALL",
                    "audioItem": {
                        "stream": {
                            "url": file.url,
                            "token": token,
                            "offsetInMilliseconds": offset
                        },
                    }
                }
            ]
        }
    }

    log(" >> LOG: START_SESSION token: {}".format(token))

    return data


@transaction.atomic()
def next_intent_response(alexa_user: AUser):
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(alexa_user.user)
    playlist_has_audio = status.playlist_has_audio.next()
    save_state_by_playlist_entry(alexa_user, playlist_has_audio)
    return start_session(playlist_has_audio)


@transaction.atomic()
def enqueue_next_song(alexa_user: AUser):
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(alexa_user.user)
    playlist_has_audio = status.playlist_has_audio.next()   # type: PlaylistHasAudio

    file = playlist_has_audio.audio

    data = {
        "version": "1.0",
        "response": {
            "shouldEndSession": True,
            "directives": [
                {
                    "type": "AudioPlayer.Play",
                    "playBehavior": "ENQUEUE",
                    "audioItem": {
                        "stream": {
                            "url": file.url,
                            "token": file.id,
                            "expectedPreviousToken": status.playlist_has_audio.audio.id,
                            "offsetInMilliseconds": 0
                        },
                    }
                }
            ]
        }
    }

    log(" >> LOG: EN.Q token: {}, previous token: {}".format(file.id, status.playlist_has_audio.audio.id))

    return data
