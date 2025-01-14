# Generated by Django 2.0.1 on 2019-05-06 08:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('actions', '0012_auto_20190330_0018'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionGeneric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('data', jsonfield.fields.JSONField(default={})),
                ('to_user', models.ForeignKey(help_text='The user that will see this act/action', on_delete=django.db.models.deletion.DO_NOTHING, related_name='request', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'action_generic',
            },
        ),
    ]
