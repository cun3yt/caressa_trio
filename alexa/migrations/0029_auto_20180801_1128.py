# Generated by Django 2.0.1 on 2018-08-01 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alexa', '0028_merge_20180731_1552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auser',
            name='alexa_user_id',
            field=models.TextField(editable=False),
        ),
    ]
