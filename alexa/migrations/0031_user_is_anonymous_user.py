# Generated by Django 2.0.1 on 2018-08-05 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alexa', '0030_auto_20180805_0129'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_anonymous_user',
            field=models.BooleanField(default=True, help_text="Having this field anonymous means that the content will not be optimized on the personal level, e.g. calling by name. Once you set the user's first name properly you can set this field to `False`"),
        ),
    ]
