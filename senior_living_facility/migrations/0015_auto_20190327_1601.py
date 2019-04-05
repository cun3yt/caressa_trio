# Generated by Django 2.0.1 on 2019-03-27 23:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields
import model_utils.fields
import utilities.views.mixins


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('senior_living_facility', '0014_auto_20190327_1403'),
    ]

    operations = [
        migrations.CreateModel(
            name='MockMessageThread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('senior', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'mock_message_thread',
            },
            bases=(models.Model, utilities.views.mixins.ForAdminApplicationMixin),
        ),
        migrations.RenameField(
            model_name='seniorlivingfacilitymockmessagedata',
            old_name='last_message',
            new_name='message',
        ),
        migrations.AddField(
            model_name='seniorlivingfacilitymockmessagedata',
            name='message_from',
            field=jsonfield.fields.JSONField(default={}),
        ),
    ]