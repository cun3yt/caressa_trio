# Generated by Django 2.0.1 on 2019-05-20 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('senior_living_facility', '0028_auto_20190519_0314'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['-created'], name='message_created_af91fe_idx'),
        ),
    ]
