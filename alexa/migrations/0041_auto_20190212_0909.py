# Generated by Django 2.0.1 on 2019-02-12 17:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alexa', '0040_auto_20190202_1318'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auser',
            name='user',
        ),
        migrations.RemoveField(
            model_name='auseremotionalstate',
            name='user',
        ),
        migrations.RemoveField(
            model_name='ausermedicalstate',
            name='user',
        ),
        migrations.RemoveField(
            model_name='enginesession',
            name='user',
        ),
        migrations.RemoveField(
            model_name='request',
            name='user',
        ),
        migrations.RemoveField(
            model_name='session',
            name='alexa_user',
        ),
        migrations.RemoveField(
            model_name='user',
            name='hardware',
        ),
        migrations.DeleteModel(
            name='AUser',
        ),
        migrations.DeleteModel(
            name='AUserEmotionalState',
        ),
        migrations.DeleteModel(
            name='AUserMedicalState',
        ),
        migrations.DeleteModel(
            name='EngineSession',
        ),
        migrations.DeleteModel(
            name='Request',
        ),
    ]