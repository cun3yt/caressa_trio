# Generated by Django 2.0.1 on 2019-04-03 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0023_auto_20190331_1756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audiofile',
            name='url',
            field=models.URLField(db_index=True, help_text='File URL, it must be publicly accessible', verbose_name='File URL'),
        ),
    ]
