from django.views.decorators.csrf import csrf_exempt
import json
from utilities.dictionaries import deep_get
from utilities.logger import log
from alexa.models import AUser, User, Session
from datetime import datetime
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from streaming.models import PlaylistHasAudio, UserPlaylistStatus, TrackingAction, AudioFile
from django.db import transaction


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
    return JsonResponse(response_body)


def save_action(a_user: AUser, session: Session, segment0, segment1):
    action = TrackingAction(user=a_user.user,
                            session=session,
                            segment0=segment0,
                            segment1=segment1)
    action.save()


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

    if req_type in ['LaunchRequest', 'PlaybackController.PlayCommandIssued', ] \
            or intent_name in ['AMAZON.ResumeIntent', ]:
        save_action(alexa_user, sess, (req_type if req_type else intent_name), 'resume_session')
        return resume_session(alexa_user)
    elif req_type in ['PlaybackController.NextCommandIssued', ] or intent_name in ['AMAZON.NextIntent', ]:
        save_action(alexa_user, sess, (req_type if req_type else intent_name), 'next_intent_response')
        return next_intent_response(alexa_user)
    elif req_type in ['AudioPlayer.PlaybackNearlyFinished', ]:
        save_action(alexa_user, sess, req_type, 'enqueue_next_song')
        return enqueue_next_song(alexa_user)
    elif req_type in ['AudioPlayer.PlaybackStarted', ]:
        save_action(alexa_user, sess, req_type, 'filler')
        save_state(alexa_user, req_body)
        return filler()
    elif req_type in ['PlaybackController.PauseCommandIssued', ] or intent_name in ['AMAZON.PauseIntent', ]:
        save_action(alexa_user, sess, (req_type if req_type else intent_name), 'pause_session')
        return pause_session(alexa_user)
    elif intent is not None:
        save_action(alexa_user, sess, intent_name, 'stop_session')
        return stop_session()

    save_action(alexa_user, sess, 'fallback_state', 'filler')
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
def save_state(alexa_user: AUser, req_body):        # todo Problematic!! fix the token logic below..
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(alexa_user.user)
    offset = deep_get(req_body, 'context.AudioPlayer.offsetInMilliseconds')
    token = deep_get(req_body, 'context.AudioPlayer.token')     # this is AudioFile instance's ID

    qs_playlist_entry = status.playlist_has_audio.playlist.playlisthasaudio_set.filter(
        audio_id__exact=token, order_id__gte=status.playlist_has_audio.order_id # todo : token needs to be playlist-has-audio.id
    )

    new_playlist_has_audio = None
    if qs_playlist_entry.count() < 1:   # if the currently playing song is not available in the playlist
        new_playlist_has_audio = status.playlist_has_audio.playlist.playlisthasaudio_set.all()[0]
    else:
        new_playlist_has_audio = qs_playlist_entry[0]

    # token (i.e. audio-id) + user-status => which p.h.a?

    status.playlist_has_audio = new_playlist_has_audio
    status.offset = offset
    status.current_active_audio = AudioFile.objects.get(id=token)
    status.save()

    log(' >> LOG SAVE_STATE: pha: {}, audio: {}, order: {}'.format(
        status.playlist_has_audio.id,
        status.playlist_has_audio.audio.id if status.playlist_has_audio.audio else status.playlist_has_audio.tag,
        status.playlist_has_audio.order_id))


@transaction.atomic()
def save_state_by_playlist_entry(alexa_user: AUser, pha: PlaylistHasAudio, audio_to_be_played: AudioFile):
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(alexa_user.user)
    status.playlist_has_audio = pha
    status.current_active_audio = audio_to_be_played
    status.offset = 0
    status.save()

    log(' >> LOG: SAVE_STATE_BY_PLAYLIST_ENTRY: pha: {}, audio/tag: {}, order: {}'.format(
        status.playlist_has_audio.id,
        status.playlist_has_audio.audio.id if status.playlist_has_audio.audio else status.playlist_has_audio.tag,
        status.playlist_has_audio.order_id))


@transaction.atomic()
def pause_session(alexa_user: AUser):
    log(' >> LOG: PAUSE')
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(alexa_user.user)
    playlist_has_audio = status.playlist_has_audio.next()
    save_state_by_playlist_entry(alexa_user, playlist_has_audio, playlist_has_audio.get_audio())
    return stop_session()


@transaction.atomic()
def resume_session(alexa_user: AUser):
    log(' >> LOG: RESUME_SESSION')
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(alexa_user.user)  # type: UserPlaylistStatus
    return start_session(status.current_active_audio, status.offset)


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


def start_session(audio_to_be_played: AudioFile, offset=0):
    token = audio_to_be_played.id

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
                            "url": audio_to_be_played.url,
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
    audio_to_be_played = playlist_has_audio.get_audio()
    save_state_by_playlist_entry(alexa_user, playlist_has_audio, audio_to_be_played)
    return start_session(audio_to_be_played)


@transaction.atomic()
def enqueue_next_song(alexa_user: AUser):
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(alexa_user.user)
    playlist_has_audio = status.playlist_has_audio.next()   # type: PlaylistHasAudio

    upcoming_file = playlist_has_audio.get_audio()

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
                            "url": upcoming_file.url,
                            "token": upcoming_file.id,
                            "expectedPreviousToken": status.current_active_audio.id,
                            "offsetInMilliseconds": 0
                        },
                    }
                }
            ]
        }
    }

    log(" >> LOG: EN.Q token: {}, previous token: {}".format(upcoming_file.id, status.current_active_audio.id))

    return data
