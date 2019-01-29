from django.views.decorators.csrf import csrf_exempt
import json
from utilities.dictionaries import deep_get
from utilities.logger import log
from alexa.models import User
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.db import transaction
from streaming.models import PlaylistHasAudio, UserPlaylistStatus, TrackingAction, Playlist, AudioFile
from scripts import replicate_playlist
from streaming.exceptions import PlaylistAlreadyExistException
from oauth2_provider.decorators import protected_resource


@csrf_exempt
@protected_resource()
def stream_io_wrapper(request):
    request_body = json.loads(request.body)
    response_body = stream_io(request_body, request)   # type: dict
    return JsonResponse(response_body)


def stream_io(req_body, request):
    # todo get TrackingAction back in a new form to keep track of users' actions
    log(req_body)
    user = request.user

    req_type = deep_get(req_body, 'request.type')
    intent = deep_get(req_body, 'request.intent')
    intent_name = deep_get(req_body, 'request.intent.name')

    log("Request Body: {}".format(req_body))
    log("Type: {}".format(req_type))
    log("Intent: {}".format(intent))
    log("Intent Name: {}".format(intent_name))

    if req_type == 'SessionEndedRequest':
        return stop_session()

    if req_type in ['LaunchRequest', 'PlaybackController.PlayCommandIssued', ] \
            or intent_name in ['AMAZON.ResumeIntent', ]:
        return resume_session(user)
    elif req_type in ['PlaybackController.NextCommandIssued', ] or intent_name in ['AMAZON.NextIntent', ]:
        return next_intent_response(user)
    elif req_type in ['AudioPlayer.PlaybackNearlyFinished', ]:
        return enqueue_next_song(user)
    elif req_type in ['AudioPlayer.PlaybackStarted', ]:
        save_state(user, req_body)
        return filler()
    elif req_type in ['PlaybackController.PauseCommandIssued', ] or intent_name in ['AMAZON.PauseIntent', ]:
        return pause_session(user)
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
def save_state(user: User, req_body):
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(user)
    offset = deep_get(req_body, 'context.AudioPlayer.offsetInMilliseconds')
    token = deep_get(req_body, 'context.AudioPlayer.token')  # token is combination of pha_hash and audio_id

    pha_and_audio_id_list = token.split(',')
    pha_hash = pha_and_audio_id_list[0]
    current_audio_file = AudioFile.objects.get(id=pha_and_audio_id_list[1])

    qs_playlist_entry = status.playlist_has_audio.playlist.playlisthasaudio_set.filter(
        hash__exact=pha_hash, order_id__gte=status.playlist_has_audio.order_id
    )

    new_playlist_has_audio = None
    if qs_playlist_entry.count() < 1:   # if the currently playing song is not available in the playlist
        new_playlist_has_audio = status.playlist_has_audio.playlist.playlisthasaudio_set.all()[0]
    else:
        new_playlist_has_audio = qs_playlist_entry[0]

    # token (i.e. audio-id) + user-status => which p.h.a?

    status.playlist_has_audio = new_playlist_has_audio
    status.offset = offset
    status.current_active_audio = current_audio_file
    status.save()

    log(' >> LOG SAVE_STATE: pha: {}, audio: {}, tag: {}, order: {}'.format(
        status.playlist_has_audio.id,
        current_audio_file.id,
        status.playlist_has_audio.audio.id if status.playlist_has_audio.audio else status.playlist_has_audio.tag,
        status.playlist_has_audio.order_id))


@transaction.atomic()
def save_state_by_playlist_entry(user: User, pha: PlaylistHasAudio, audio_to_be_played: AudioFile):
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(user)
    status.playlist_has_audio = pha
    status.current_active_audio = audio_to_be_played
    status.offset = 0
    status.save()

    log(' >> LOG: SAVE_STATE_BY_PLAYLIST_ENTRY: pha: {}, audio/tag: {}, order: {}'.format(
        status.playlist_has_audio.id,
        status.playlist_has_audio.audio.id if status.playlist_has_audio.audio else status.playlist_has_audio.tag,
        status.playlist_has_audio.order_id))


@transaction.atomic()
def pause_session(user: User):
    log(' >> LOG: PAUSE')
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(user)
    playlist_has_audio = status.playlist_has_audio.next()
    save_state_by_playlist_entry(user, playlist_has_audio, playlist_has_audio.get_audio())
    return stop_session()


@transaction.atomic()
def resume_session(user: User):
    log(' >> LOG: RESUME_SESSION')
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(user)  # type: UserPlaylistStatus
    token = '{hash},{audio_id}'.format(hash=str(status.playlist_has_audio.hash),
                                       audio_id=str(status.current_active_audio_id))
    return start_session(status.current_active_audio, token, status.offset)


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


def start_session(audio_to_be_played: AudioFile, token, offset=0):

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
def next_intent_response(user: User):
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(user)
    playlist_has_audio = status.playlist_has_audio.next()
    audio_to_be_played = playlist_has_audio.get_audio()
    save_state_by_playlist_entry(user, playlist_has_audio, audio_to_be_played)
    token = '{hash},{audio_id}'.format(hash=str(playlist_has_audio.hash),
                                       audio_id=str(audio_to_be_played.id))
    return start_session(audio_to_be_played, token)


@transaction.atomic()
def enqueue_next_song(user: User):
    status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(user)
    playlist_has_audio = status.playlist_has_audio.next()   # type: PlaylistHasAudio

    upcoming_file = playlist_has_audio.get_audio()
    upcoming_pha_hash = playlist_has_audio.hash
    token = '{hash},{audio_id}'.format(hash=str(upcoming_pha_hash), audio_id=str(upcoming_file.id))
    expected_previous_token = '{hash},{audio_id}'.format(hash=str(status.playlist_has_audio.hash),
                                                         audio_id=str(status.current_active_audio_id))
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
                            "token": token,
                            "expectedPreviousToken": expected_previous_token,
                            "offsetInMilliseconds": 0
                        },
                    }
                }
            ]
        }
    }

    log(" >> LOG: EN.Q token: {}, previous token: {}".format(token, expected_previous_token))

    return data


@transaction.atomic
def playlist_replication(request):
    playlist_to_be_copied = request.POST['playlist_name']
    target_user_id = request.POST['user_id']
    if not request.user.is_staff:
        return Http404
    try:
        replicate_playlist.run(playlist_to_be_copied, target_user_id)
    except PlaylistAlreadyExistException:
        return HttpResponseBadRequest('User Playlist already exists!')
    return HttpResponseRedirect('/admin/streaming/playlist/')

