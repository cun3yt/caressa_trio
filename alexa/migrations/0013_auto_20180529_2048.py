# Generated by Django 2.0.1 on 2018-05-29 20:48

from django.db import migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('alexa', '0012_auto_20180524_1946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ausermedicalstate',
            name='created',
            field=model_utils.fields.AutoCreatedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
    ]
