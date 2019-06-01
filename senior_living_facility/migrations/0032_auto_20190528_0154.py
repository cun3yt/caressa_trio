# Generated by Django 2.0.1 on 2019-05-28 08:54

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('senior_living_facility', '0031_seniorlivingfacilitycontent_ssml_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='seniorlivingfacility',
            name='meal_calendar_url',
            field=models.URLField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='seniorlivingfacility',
            name='mealtimes',
            field=jsonfield.fields.JSONField(default={}),
        ),
    ]