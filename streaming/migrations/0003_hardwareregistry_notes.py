# Generated by Django 2.0.1 on 2018-08-14 02:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0002_auto_20180811_0150'),
    ]

    operations = [
        migrations.AddField(
            model_name='hardwareregistry',
            name='notes',
            field=models.TextField(default=''),
        ),
    ]
