"""
Django settings for caressa project.

Generated by 'django-admin startproject' using Django 2.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import dj_database_url
import pusher
from django.contrib import admin

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

ENV = os.environ.get('ENV')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('ENV_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (ENV == 'dev')


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.herokuapp.com',
    '.ngrok.io',
    '.serveo.net',
]

HOSTED_ENV = os.environ.get('HOSTED_ENV')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django_extensions',
    'oauth2_provider',
    'rest_framework',
    'reversion',                # package `django-reversion`
    'phonenumber_field',        # package `django-phonenumber-field`
    'corsheaders',
    'utilities',
    'actstream',    # package `django activity stream`
    'admin_ordering',   # package `django-admin-ordering`
    'alexa',
    'actions',
    'streaming',
    'voice_service',
    'senior_living_facility',
]

AUTHENTICATION_BACKENDS = (
    'oauth2_provider.backends.OAuth2Backend',
    # Uncomment following if you want to access the admin
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'caressa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'caressa.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASE_ENV_VARIABLE = 'ACTUAL_DATABASE_URL'
DATABASES = {
    'default': dj_database_url.config(env=DATABASE_ENV_VARIABLE,
                                      conn_max_age=600, )
}

AUTH_USER_MODEL = 'alexa.User'

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_WHITELIST = tuple(os.getenv('CORS_ORIGIN_WHITELIST').split(','))
# ^^^ These lines are needed to be configured for each developer who is trying to debug the app in his/her phone according to their local requirements


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static_files_compiled')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
    os.path.join(BASE_DIR, "static"),
)

SITE_ID = 1

ACTSTREAM_SETTINGS = {
    'MANAGER': 'alexa.managers.ActionManagerByCircle',
    'FETCH_RELATIONS': True,
    'USE_PREFETCH': True,
    'USE_JSONFIELD': True,
    'GFK_FETCH_DEPTH': 1,
}

OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
        'groups': 'Access to your groups',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    },
    'DEFAULT_PAGINATION_CLASS': 'alexa.api.configuration.pagination.ExtendedPageNumberPagination',
    'PAGE_SIZE': 5,
}

DB_DEBUG = os.environ.get('DB_DEBUG', False)

if DB_DEBUG:
    LOGGING = {
        'version': 1,
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
            },
        },
    }

# Pusher ENV variables
pusher_app_id = os.environ.get('PUSHER_APP_ID')
pusher_key_id = os.environ.get('PUSHER_KEY')
pusher_secret = os.environ.get('PUSHER_SECRET')
pusher_cluster = os.environ.get('PUSHER_CLUSTER')
pusher_client = pusher.Pusher(app_id=pusher_app_id, key=pusher_key_id, secret=pusher_secret, cluster=pusher_cluster)

# AWS ENV variables
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
MEDIA_BUCKET = os.environ.get('MEDIA_BUCKET')
S3_RAW_UPLOAD_BUCKET = 'caressa-upload'
S3_PRODUCTION_BUCKET = 'caressa-prod'
S3_REGION = 'https://s3-us-west-1.amazonaws.com'

CONVERSATION_ENGINES = {
    'ttl': 10*60,
}

admin.site.empty_value_display = '-empty-'

WEB_CLIENT = {
    'id': os.getenv('WEB_CLIENT_ID'),
    'secret': os.getenv('WEB_CLIENT_SECRET'),
}
