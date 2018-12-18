# Generated by Django 2.0.1 on 2018-10-16 21:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('streaming', '0009_auto_20181001_1108'),
    ]

    operations = [
        migrations.CreateModel(
            name='VoiceMessageStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('key', models.TextField(help_text='File name that will be listened by destination')),
                ('list_status', models.CharField(choices=[('listened', 'Listened'), ('waiting', 'Waiting')], default='waiting', max_length=50)),
                ('destination', models.ForeignKey(help_text='Voice Destination User', on_delete=django.db.models.deletion.DO_NOTHING, related_name='voice_destination_user', to=settings.AUTH_USER_MODEL)),
                ('source', models.ForeignKey(help_text='Voice Source User', on_delete=django.db.models.deletion.DO_NOTHING, related_name='voice_source_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'voice_message_status',
            },
        ),
    ]