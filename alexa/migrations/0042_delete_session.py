# Generated by Django 2.0.1 on 2019-02-12 17:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alexa', '0041_auto_20190212_0909'),
        ('streaming', '0012_auto_20190212_0909'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Session',
        ),
    ]
