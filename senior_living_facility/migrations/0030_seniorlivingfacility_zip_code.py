# Generated by Django 2.0.1 on 2019-05-23 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('senior_living_facility', '0029_auto_20190520_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='seniorlivingfacility',
            name='zip_code',
            field=models.CharField(blank=True, default='', max_length=5),
        ),
    ]
