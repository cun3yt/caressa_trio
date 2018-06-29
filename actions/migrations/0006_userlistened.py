# Generated by Django 2.0.1 on 2018-06-28 01:20

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0005_userpost'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserListened',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('action', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='actions.UserAction')),
            ],
            options={
                'db_table': 'user_listened',
            },
        ),
    ]