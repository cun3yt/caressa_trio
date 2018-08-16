# Generated by Django 2.0.1 on 2018-08-10 23:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AudioFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('audio_type', models.CharField(choices=[('song', 'Song'), ('podcast', 'Podcast'), ('news', 'News'), ('joke', 'Joke'), ('fact', 'Fact'), ('family_update', 'Family Update'), ('miscellaneous', 'Miscellaneous')], max_length=50)),
                ('url', models.TextField(help_text='File URL, it must be publicly accessible')),
                ('duration', models.IntegerField(default=0, help_text='Duration of content in seconds')),
                ('name', models.TextField(help_text='For internal use only')),
                ('description', models.TextField(blank=True, default='', help_text='For Internal Use only')),
                ('payload', jsonfield.fields.JSONField(default={})),
            ],
            options={
                'db_table': 'audio_file',
            },
        ),
        migrations.CreateModel(
            name='HardwareRegistry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('caressa_device_id', models.CharField(max_length=100)),
                ('device_id', models.TextField()),
            ],
            options={
                'db_table': 'hardware_registry',
            },
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.TextField(blank=True, db_index=True, default='', help_text='Playlist name')),
            ],
            options={
                'db_table': 'playlist',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='PlaylistHasAudio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('order_id', models.FloatField(db_index=True)),
                ('audio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streaming.AudioFile')),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='streaming.Playlist')),
            ],
            options={
                'db_table': 'playlist_has_audio',
                'ordering': ['order_id'],
            },
        ),
        migrations.CreateModel(
            name='UserPlaylistStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('offset', models.IntegerField(default=0, help_text='The place user left the song in milliseconds')),
                ('playlist_has_audio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='streaming.PlaylistHasAudio')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_playlist_status',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='playlist',
            name='audio_files',
            field=models.ManyToManyField(through='streaming.PlaylistHasAudio', to='streaming.AudioFile'),
        ),
        migrations.AddField(
            model_name='playlist',
            name='user',
            field=models.ForeignKey(help_text='Who is it for?', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]