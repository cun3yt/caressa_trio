from django.views.decorators.csrf import csrf_exempt
import json
from utilities.dictionaries import deep_get
from utilities.logger import log
from alexa.models import User
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.db import transaction
from streaming.models import AudioFile, UserAudioStatus
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
    status, _ = UserAudioStatus.get_user_audio_status_for_user(user)
    offset = deep_get(req_body, 'context.AudioPlayer.offsetInMilliseconds')
    token = deep_get(req_body, 'context.AudioPlayer.token')  # token is audio id

    current_audio_file_qs = AudioFile.objects.all().filter(id=token)

    if current_audio_file_qs.count() < 1:   # if the currently playing song is not available in the AudioFile
        current_audio_file = user.get_audio
    else:
        current_audio_file = current_audio_file_qs[0]

    status.current_active_audio = current_audio_file
    status.offset = offset
    status.save()

    log(' >> LOG SAVE_STATE: audio: {}'.format(current_audio_file.id))


@transaction.atomic()
def save_state_by_audio(user: User, audio_to_be_played: AudioFile):
    status, _ = UserAudioStatus.get_user_audio_status_for_user(user)
    status.current_active_audio = audio_to_be_played
    status.offset = 0
    status.save()

    log(' >> LOG: SAVE_STATE_BY_NEXT_TAGGED_AUDIO: \nAudio{} \nTags: {} \n'.format(audio_to_be_played.name,
                                                                                   audio_to_be_played.tag_list))


@transaction.atomic()
def pause_session(user: User):
    log(' >> LOG: PAUSE')
    save_state_by_audio(user, user.get_audio)
    return stop_session()


@transaction.atomic()
def resume_session(user: User):
    log(' >> LOG: RESUME_SESSION')
    status, _ = UserAudioStatus.get_user_audio_status_for_user(user)  # type: UserAudioStatus
    return start_session(status.current_active_audio, offset=0)


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
                            "token": audio_to_be_played.id,
                            "offsetInMilliseconds": offset
                        },
                    }
                }
            ]
        }
    }

    log(" >> LOG: START_SESSION \nName: {} \nURL: {} \nTags: {}".format(audio_to_be_played.name,
                                                                        audio_to_be_played.url,
                                                                        audio_to_be_played.tag_list))

    return data


@transaction.atomic()
def next_intent_response(user: User):
    audio_to_be_played = user.get_audio
    save_state_by_audio(user, audio_to_be_played)
    return start_session(audio_to_be_played)


@transaction.atomic()
def enqueue_next_song(user: User):
    upcoming_file = user.get_audio
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
                            "expectedPreviousToken": 0,
                            "offsetInMilliseconds": 0
                        },
                    }
                }
            ]
        }
    }

    log(" >> LOG: Playing audio \nName: {} \nURL: {} \nTags: {}".format(upcoming_file.name,
                                                                        upcoming_file.url,
                                                                        upcoming_file.tag_list))

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

