# Generated by Django 2.0.1 on 2019-03-27 19:44

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
        ('senior_living_facility', '0012_seniorlivingfacilitymockuserdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='SeniorLivingFacilityMockMessageData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('last_message', jsonfield.fields.JSONField(default={})),
                ('senior', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'mock_facility_messages',
            },
            bases=(models.Model, utilities.views.mixins.ForAdminApplicationMixin),
        ),
    ]
