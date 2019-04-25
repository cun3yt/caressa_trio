# Generated by Django 2.0.1 on 2019-04-24 00:13

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('senior_living_facility', '0023_auto_20190412_1930'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('date', models.DateField(default=datetime.date.today, help_text="This date represents when the photo taken. If date can't be extracted from photo's metadata it will be set to today by default.")),
                ('url', models.URLField(help_text='Photo URL, it must be publicly accessible', verbose_name='Photo URL')),
            ],
            options={
                'db_table': 'photo',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='PhotoGallery',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('senior_living_facility', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='senior_living_facility.SeniorLivingFacility')),
            ],
            options={
                'db_table': 'photo_gallery',
            },
        ),
        migrations.AddField(
            model_name='photo',
            name='photo_gallery',
            field=models.ForeignKey(help_text='The gallery which the photo belongs to.', on_delete=django.db.models.deletion.DO_NOTHING, to='senior_living_facility.PhotoGallery'),
        ),
    ]