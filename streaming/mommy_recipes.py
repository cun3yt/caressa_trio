from model_mommy.recipe import Recipe, seq, foreign_key
from streaming.models import AudioFile, Playlist, PlaylistHasAudio, UserPlaylistStatus, TrackingAction
from alexa.mommy_recipes import user, session_recipe

audio_file_recipe = Recipe(
    AudioFile,
    audio_type='song',
    url='http://www.example.com/audio/song.mp3',
    duration=seq(12),
    name=seq('song'),
    description=seq('some description')
)

playlist_recipe = Recipe(
    Playlist,
    user=foreign_key(user),
    name='playlist',
)

playlist_has_audio_recipe = Recipe(
    PlaylistHasAudio,
    playlist=foreign_key(playlist_recipe),
    order_id=seq(10.0),
    audio=foreign_key(audio_file_recipe)
)

user_playlist_status_recipe = Recipe(
    UserPlaylistStatus,
    user=foreign_key(user),
    playlist_has_audio=foreign_key(playlist_has_audio_recipe),
    current_active_audio=foreign_key(audio_file_recipe),
)

tracking_action_recipe = Recipe(
    TrackingAction,
    user=foreign_key(user),
    session=foreign_key(session_recipe),
    segment0='{}',
    segment1='{}',
    segment2='{}',
    segment3='{}',
)
