# Generated by Django 2.0.1 on 2018-05-08 23:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alexa', '0003_auto_20180508_2320'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userfollowuser',
            name='from_user',
        ),
        migrations.RemoveField(
            model_name='userfollowuser',
            name='to_user',
        ),
        migrations.DeleteModel(
            name='UserFollowUser',
        ),
    ]
