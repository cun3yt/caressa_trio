# Generated by Django 2.0.1 on 2018-08-02 22:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('actions', '0006_userlistened'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManualUserPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('content_to_be_spoken', models.TextField(help_text='The content to be spoken on Alexa. Put {timeago} for time past since `Content Creation Time`')),
                ('content_creation_time', models.DateTimeField(help_text='The date/time that the user content was created (e.g. Facebook post time)')),
                ('yes_no_question', models.TextField(help_text='Yes/No question that is presented after the content is spoken on Alexa.')),
                ('yes_reflection_on_circle', models.TextField(help_text='The presentation of the Alexa user\'s yes response to the circle if "Yes" is said. ')),
                ('is_published', models.BooleanField(default=False, help_text='The post will not be presented on Alexa until it is published')),
                ('listened_time', models.DateTimeField(db_index=True, default=None, help_text="When the central person (e.g. senior) listened the content. Once the content is listened, it will not be spoken again. If you'd like to re-publish a spoken content, create a new manual post instead of re-publishing it", null=True)),
                ('user', models.ForeignKey(help_text='Who (the circle member) is the content about?', on_delete=django.db.models.deletion.DO_NOTHING, related_name='manual_posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'manual_user_post',
            },
        ),
    ]