# Generated by Django 2.0.1 on 2019-03-22 02:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0016_usermaincontentconsumption'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playlist',
            name='audio_files',
        ),
        migrations.RemoveField(
            model_name='playlist',
            name='user',
        ),
        migrations.RemoveField(
            model_name='playlisthasaudio',
            name='audio',
        ),
        migrations.RemoveField(
            model_name='playlisthasaudio',
            name='playlist',
        ),
        migrations.RemoveField(
            model_name='userplayliststatus',
            name='current_active_audio',
        ),
        migrations.RemoveField(
            model_name='userplayliststatus',
            name='playlist_has_audio',
        ),
        migrations.RemoveField(
            model_name='userplayliststatus',
            name='user',
        ),
        migrations.RemoveField(
            model_name='usermaincontentconsumption',
            name='modified',
        ),
        migrations.DeleteModel(
            name='Playlist',
        ),
        migrations.DeleteModel(
            name='PlaylistHasAudio',
        ),
        migrations.DeleteModel(
            name='UserPlaylistStatus',
        ),
    ]
