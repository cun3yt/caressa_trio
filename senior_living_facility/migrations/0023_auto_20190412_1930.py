# Generated by Django 2.0.1 on 2019-04-13 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('senior_living_facility', '0022_auto_20190412_1919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facilitycheckinoperationforsenior',
            name='checked',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
