# Generated by Django 2.0.1 on 2018-07-25 04:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alexa', '0026_merge_20180721_0100'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fact',
            name='type',
        ),
        migrations.AddField(
            model_name='fact',
            name='fact_type',
            field=models.ForeignKey(db_column='type', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='facts', to='alexa.FactType'),
        ),
    ]
