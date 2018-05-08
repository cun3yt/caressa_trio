# Generated by Django 2.0.1 on 2018-05-02 20:25

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('alexa', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auser',
            name='profile',
            field=jsonfield.fields.JSONField(default={}),
        ),
        migrations.AlterField(
            model_name='ausermedicalstate',
            name='data',
            field=jsonfield.fields.JSONField(default={}),
        ),
        migrations.AlterField(
            model_name='enginesession',
            name='data',
            field=jsonfield.fields.JSONField(default={}),
        ),
    ]
