# Generated by Django 2.0.1 on 2019-01-22 21:45

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('alexa', '0037_auto_20190122_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='familyprospect',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.AlterField(
            model_name='familyprospect',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128),
        ),
    ]
