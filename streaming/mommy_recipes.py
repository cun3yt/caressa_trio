from model_mommy.recipe import Recipe, seq, foreign_key, related
from streaming.models import AudioFile, Tag, Playlist, PlaylistHasAudio
from alexa.mommy_recipes import user


tag_recipe = Recipe(
    Tag,
    name='tag1'
)

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