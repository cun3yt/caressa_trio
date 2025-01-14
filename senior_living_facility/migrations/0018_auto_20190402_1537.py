# Generated by Django 2.0.1 on 2019-04-02 22:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0026_audiofile_hash'),
        ('senior_living_facility', '0017_servicerequest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seniorlivingfacilitycontent',
            name='audio_url',
        ),
        migrations.RemoveField(
            model_name='seniorlivingfacilitycontent',
            name='text_content_hash',
        ),
        migrations.AddField(
            model_name='seniorlivingfacilitycontent',
            name='audio_file',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='streaming.AudioFile'),
        ),
    ]
