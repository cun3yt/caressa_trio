# Generated by Django 2.0.1 on 2019-02-02 23:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('senior_living_facility', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SeniorDevice',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('serial', models.CharField(blank=True, default='', max_length=50, primary_key=True, serialize=False)),
                ('is_online', models.BooleanField(default=False)),
                ('status_checked', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'Senior Device',
                'verbose_name_plural': 'Senior Devices',
                'db_table': 'senior_device',
            },
        ),
        migrations.CreateModel(
            name='SeniorDevicesRawLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('data', jsonfield.fields.JSONField(default={})),
            ],
            options={
                'verbose_name': "Senior Devices' Raw Log",
                'verbose_name_plural': "Senior Devices' Raw Logs",
                'db_table': 'senior_devices_raw_log',
            },
        ),
        migrations.AddField(
            model_name='seniordevice',
            name='raw_log',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='senior_living_facility.SeniorDevicesRawLog'),
        ),
        migrations.AddField(
            model_name='seniordevice',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]
