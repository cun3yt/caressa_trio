# Generated by Django 2.0.1 on 2018-11-15 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('senior_living_facility', '0002_seniorlivingfacility_timezone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seniorlivingfacility',
            name='calendar',
        ),
        migrations.AddField(
            model_name='seniorlivingfacility',
            name='calendar_url',
            field=models.URLField(default=None, null=True),
        ),
    ]
