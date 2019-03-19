from django.views.decorators.csrf import csrf_exempt
import json
from utilities.dictionaries import deep_get
from utilities.logger import log
from alexa.models import User
from django.http import JsonResponse
from django.db import transaction
from streaming.models import AudioFile, UserMainContentConsumption
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
        save_played_main_content(user, req_body)
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
def save_played_main_content(user: User, req_body):
    token = deep_get(req_body, 'context.AudioPlayer.token')
    main_content = AudioFile.objects.get(pk=token)
    UserMainContentConsumption.objects.create(user=user, played_main_content=main_content)

    log(' >> LOG: SAVE_STATE_BY_NEXT_TAGGED_AUDIO: \nAudio{} \nTags: {} \n'.format(main_content.name,
                                                                                   main_content.tag_list))


@transaction.atomic()
def pause_session():
    log(' >> LOG: PAUSE')
    return stop_session()


@transaction.atomic()
def resume_session(user: User):
    log(' >> LOG: RESUME_SESSION')
    main_content_to_be_played = AudioFile.get_main_content_to_play(user)
    return start_session(main_content_to_be_played, offset=0)


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


def start_session(main_content_to_be_played: AudioFile, offset=0):

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
                            "url": main_content_to_be_played.url,
                            "token": main_content_to_be_played.id,
                            "offsetInMilliseconds": offset
                        },
                    }
                }
            ]
        }
    }

    log(" >> LOG: START_SESSION \nName: {} \nURL: {} \nTags: {}".format(main_content_to_be_played.name,
                                                                        main_content_to_be_played.url,
                                                                        main_content_to_be_played.tag_list))

    return data


@transaction.atomic()
def next_intent_response(user: User):
    audio_to_be_played = AudioFile.get_main_content_to_play(user)
    return start_session(audio_to_be_played)


@transaction.atomic()
def enqueue_next_song(user: User):
    main_content_to_be_played = AudioFile.get_main_content_to_play(user)
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
                            "url": main_content_to_be_played.url,
                            "token": main_content_to_be_played.id,
                            "expectedPreviousToken": 0,
                            "offsetInMilliseconds": 0
                        },
                    }
                }
            ]
        }
    }

    log(" >> LOG: Playing audio \nName: {} \nURL: {} \nTags: {}".format(main_content_to_be_played.name,
                                                                        main_content_to_be_played.url,
                                                                        main_content_to_be_played.tag_list))

    return data
