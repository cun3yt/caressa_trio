# Generated by Django 2.0.1 on 2019-04-02 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0025_auto_20190402_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='audiofile',
            name='hash',
            field=models.TextField(blank=True, db_index=True, default=''),
        ),
    ]
