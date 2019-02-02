# Generated by Django 2.0.1 on 2019-02-02 21:18

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('alexa', '0039_familyoutreach'),
    ]

    operations = [
        migrations.AlterField(
            model_name='familyoutreach',
            name='tracking_code',
            field=models.UUIDField(db_index=True, default=uuid.uuid4),
        ),
    ]