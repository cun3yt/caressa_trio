# Generated by Django 2.0.1 on 2018-07-20 19:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('alexa', '0023_song_song_owner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='song',
            name='song_location',
        ),
        migrations.RemoveField(
            model_name='song',
            name='song_name',
        ),
        migrations.RemoveField(
            model_name='song',
            name='song_owner',
        ),
        migrations.AddField(
            model_name='song',
            name='artist',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='song',
            name='duration',
            field=models.PositiveIntegerField(default=79),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='song',
            name='file_name',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='song',
            name='title',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
