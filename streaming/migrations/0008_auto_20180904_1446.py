# Generated by Django 2.0.1 on 2018-09-04 21:46

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0007_auto_20180825_0352'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'tag',
            },
        ),
        migrations.AddField(
            model_name='playlisthasaudio',
            name='hash',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AddField(
            model_name='playlisthasaudio',
            name='tag',
            field=models.TextField(blank=True, default='', help_text='If there is an audio file specified in "Audio" section, these tags are going to be ignored!'),
        ),
        migrations.AddField(
            model_name='userplayliststatus',
            name='current_active_audio',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='streaming.AudioFile'),
        ),
        migrations.AlterField(
            model_name='playlisthasaudio',
            name='audio',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='streaming.AudioFile'),
        ),
        migrations.AddField(
            model_name='audiofile',
            name='tags',
            field=models.ManyToManyField(to='streaming.Tag'),
        ),
    ]
