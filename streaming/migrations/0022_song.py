# Generated by Django 2.0.1 on 2019-03-31 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0021_auto_20190329_1624'),
    ]

    operations = [
        migrations.CreateModel(
            name='Song',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('streaming.audiofile',),
        ),
    ]
