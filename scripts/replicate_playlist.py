from streaming.models import Playlist, PlaylistHasAudio, UserPlaylistStatus
from alexa.models import User
from utilities.logger import log
from django.db import transaction


def update_user_status_for_new_playlist(status: UserPlaylistStatus, new_playlist):
    audio_pointed = status.playlist_has_audio.audio
    status.playlist_has_audio = new_playlist.playlisthasaudio_set.filter(audio=audio_pointed).all()[0]
    status.save()


@transaction.atomic
def run(playlist_name, user_id):
    """
    Sample usage: `./manage.py runscript replicate_playlist --script-args cold-start 1`
    """
    from_playlist = Playlist.objects.filter(name__iexact=playlist_name)[0]
    user = User.objects.filter(id=user_id)[0]

    log("Replicating the playlist {} for user {}".format(from_playlist.name, user.get_full_name()))

    if Playlist.objects.filter(user=user).count() > 0:
        log('User Playlist already exists! Ending script')
        raise Exception('User Playlist already exists!')

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

    if created:
        log('UserPlaylistStatus entry didn\'t exist, created a new one')
        return

    update_user_status_for_new_playlist(status, to_playlist)
