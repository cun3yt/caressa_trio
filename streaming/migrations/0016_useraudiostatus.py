# Generated by Django 2.0.1 on 2019-03-18 05:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('streaming', '0015_auto_20190302_1830'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAudioStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('current_active_audio', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='streaming.AudioFile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_audio_status',
                'ordering': ['id'],
            },
        ),
    ]
