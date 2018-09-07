from django.views.decorators.csrf import csrf_exempt
import json
from utilities.dictionaries import deep_get
from utilities.logger import log
from alexa.models import AUser, User, Session
from datetime import datetime
from django.utils.crypto import get_random_string
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.db import transaction
from streaming.models import PlaylistHasAudio, UserPlaylistStatus, TrackingAction, Playlist
from alexa.models import User


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
    if not status.playlist_has_audio.is_current_content_time_fit():
        next_content = status.playlist_has_audio.next()
        save_state_by_playlist_entry(alexa_user, next_content)
        updated_status, _ = UserPlaylistStatus.get_user_playlist_status_for_user(alexa_user.user)  # type: UserPlaylistStatus
        return start_session(updated_status.playlist_has_audio, status.offset)
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


def update_user_status_for_new_playlist(status: UserPlaylistStatus, new_playlist):
    audio_pointed = status.playlist_has_audio.audio
    status.playlist_has_audio = new_playlist.playlisthasaudio_set.filter(audio=audio_pointed).all()[0]
    status.save()


@transaction.atomic
def replicate_playlist(request):
    playlist_name = request.POST['playlist_name']
    user_id = request.POST['user_id']

    if not request.user.is_staff:
        return Http404

    log('ARG as Playlist name : {} ARG as user id : {}'.format(playlist_name, user_id))
    from_playlist = Playlist.objects.filter(name__iexact=playlist_name)[0]
    user = User.objects.filter(id=user_id)[0]

    log("Replicating the playlist {} for user {}".format(from_playlist.name, user.get_full_name()))

    if Playlist.objects.filter(user=user).count() > 0:
        log('User Playlist already exists! Ending script')
        return HttpResponseBadRequest('User Playlist already exists!')

    to_playlist = Playlist(user=user, name='user-{}-playlist'.format(user.id))
    to_playlist.save()
    log('Playlist created')

    number_of_entries = from_playlist.playlisthasaudio_set.count()
    log('Number of entries to copy: {}'.format(number_of_entries))

    for index, entry in enumerate(from_playlist.playlisthasaudio_set.all()):
        log(' {}/{} is being copied'.format(index+1, number_of_entries))
        entry.pk = None
        entry.playlist = to_playlist
        entry.save()

    log('Playlist successfully copied')

    status, created = UserPlaylistStatus.get_user_playlist_status_for_user(user)    # type: UserPlaylistStatus
    update_user_status_for_new_playlist(status, to_playlist)

    if created:
        log('UserPlaylistStatus entry didn\'t exist, created a new one')
        return HttpResponseRedirect('/admin/streaming/playlist/')

