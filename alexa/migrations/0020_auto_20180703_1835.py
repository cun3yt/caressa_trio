# Generated by Django 2.0.1 on 2018-07-03 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alexa', '0019_auto_20180620_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enginesession',
            name='state',
            field=models.TextField(blank=True, db_index=True),
        ),
    ]
