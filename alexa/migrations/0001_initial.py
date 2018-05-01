# Generated by Django 2.0.1 on 2018-05-01 18:59

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import phonenumber_field.modelfields
import stream_django.activity


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('user_type', models.TextField(choices=[('SENIOR', 'Senior'), ('FAMILY', 'Family Member'), ('CAREGIVER', 'Caregiver'), ('CAREGIVER_ORG', 'Caregiver Organization')], default='SENIOR')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, db_index=True, max_length=128)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('alexa_id', models.TextField(db_index=True, editable=False)),
                ('engine_schedule', models.TextField(blank=True, default='')),
                ('profile', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='a_users', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'a_user',
            },
        ),
        migrations.CreateModel(
            name='AUserEmotionalState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('attribute', model_utils.fields.StatusField(choices=[('happiness', 'happiness'), ('anxiety', 'anxiety'), ('delusional', 'delusional'), ('loneliness', 'loneliness')], db_index=True, default='happiness', max_length=100, no_check_for_status=True)),
                ('value', models.DecimalField(decimal_places=2, max_digits=5)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='emotional_states', to='alexa.AUser')),
            ],
            options={
                'db_table': 'a_user_emotional_state',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='AUserMedicalState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('measurement', model_utils.fields.StatusField(choices=[('blood_pressure', 'blood_pressure')], db_index=True, default='blood_pressure', max_length=100, no_check_for_status=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='medical_state', to='alexa.AUser')),
            ],
            options={
                'db_table': 'a_user_medical_state',
            },
        ),
        migrations.CreateModel(
            name='EngineSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.TextField()),
                ('state', models.TextField(blank=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='engine_sessions', to='alexa.AUser')),
            ],
            options={
                'db_table': 'a_engine_session',
            },
        ),
        migrations.CreateModel(
            name='Joke',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('main', models.TextField()),
                ('punchline', models.TextField()),
            ],
            options={
                'db_table': 'joke',
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('handler_engine', models.TextField(blank=True, default='')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='requests', to='alexa.AUser')),
            ],
            options={
                'db_table': 'a_request',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('alexa_id', models.TextField(db_index=True, editable=False)),
                ('alexa_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='alexa.AUser')),
            ],
            options={
                'db_table': 'a_session',
            },
        ),
        migrations.CreateModel(
            name='UserActOnContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('verb', models.TextField(db_index=True)),
                ('object', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_actions_on_content', to='alexa.Joke')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='contents_user_acted_on', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_act_on_content',
            },
            bases=(models.Model, stream_django.activity.Activity),
        ),
        migrations.CreateModel(
            name='UserFollowUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('from_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='following', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='followed_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_follow_user',
            },
        ),
    ]
