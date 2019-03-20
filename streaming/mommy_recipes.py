from model_mommy.recipe import Recipe, seq
from streaming.models import AudioFile

audio_file_recipe = Recipe(
    AudioFile,
    audio_type='song',
    url=seq('http://www.example.com/audio/song.mp3'),
    duration=seq(12),
    name=seq('song'),
    description=seq('some description')
)
