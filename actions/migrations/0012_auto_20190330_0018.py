# Generated by Django 2.0.1 on 2019-03-30 07:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0011_auto_20190306_1547'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='manualuserpost',
            name='user',
        ),
        migrations.DeleteModel(
            name='ManualUserPost',
        ),
    ]
