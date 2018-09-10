# Generated by Django 2.0.1 on 2018-08-25 10:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('alexa', '0031_user_is_anonymous_user'),
        ('streaming', '0006_auto_20180820_1516'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackingAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('segment0', models.CharField(default=None, max_length=100, null=True)),
                ('segment1', models.CharField(default=None, max_length=100, null=True)),
                ('segment2', models.CharField(default=None, max_length=100, null=True)),
                ('segment3', models.CharField(default=None, max_length=100, null=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='alexa.Session')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tracking_action',
            },
        ),
        migrations.AlterField(
            model_name='playlisthasaudio',
            name='play_time',
            field=models.TextField(choices=[('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening'), ('night', 'Night'), ('daylong', 'Daylong')], default='daylong'),
        ),
        migrations.AddIndex(
            model_name='trackingaction',
            index=models.Index(fields=['segment0', 'segment1', 'segment2', 'segment3'], name='tracking_ac_segment_a532c2_idx'),
        ),
    ]