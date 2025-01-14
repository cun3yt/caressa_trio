from os.path import (
    join as path_join,
    dirname,
    abspath,
    normpath as path_normpath,
)
from os import environ
import dj_database_url
from django.contrib import admin
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = dirname(dirname(abspath(__file__)))
UPLOADS_DIR = path_normpath(path_join(BASE_DIR, 'uploads/'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

ENV = environ.get('ENV')

# Production specific changes
if ENV == 'prod':
    s3_bucket_name = 'caressa-prod'
else:
    s3_bucket_name = 'caressa-dev'


# Test stubs are here, todo: conditional imports can be done similar to how it is done in the hardware code
if ENV == 'test':
    from utilities.test_stubs import pusher
else:
    import pusher


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ.get('ENV_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (ENV == 'dev')


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.herokuapp.com',
    '.ngrok.io',
    '.serveo.net',
]

SUPPORT_EMAIL_ACCOUNTS = [
    'mikail@caressa.ai',
    'cuneyt@caressa.ai',
]

HOSTED_ENV = environ.get('HOSTED_ENV')

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
    'content_services',
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
        'DIRS': [path_join(BASE_DIR, 'templates/')],
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

CORS_ORIGIN_WHITELIST = tuple(environ.get('CORS_ORIGIN_WHITELIST', '').split(','))
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

STATIC_ROOT = path_normpath(path_join(BASE_DIR, 'static_files_compiled/'))
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    path_normpath(path_join(BASE_DIR, 'static/')),
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

API_URL = environ.get('API_URL')
WEB_BASE_URL = environ.get('WEB_BASE_URL')

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
        'anon': '100000/day',
        'user': '1000000/day'
    },
    'DEFAULT_PAGINATION_CLASS': 'alexa.api.configuration.pagination.ExtendedPageNumberPagination',
    'PAGE_SIZE': 5,
    'DATETIME_ZONE_FORMAT': '%Y-%m-%d %H:%M:%S%z',      # todo: Should we unify all time ops with this or epoch?
}

DB_DEBUG = environ.get('DB_DEBUG', False)

if DB_DEBUG:
    LOGGING = {
        'version': 1,
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
            },
        },
    }

CACHE_DEFAULT_TIMEOUT = 7200

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'z_cache_table',
        'TIMEOUT': CACHE_DEFAULT_TIMEOUT,
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
        }
    }
}

# Pusher ENV variables
pusher_app_id = environ.get('PUSHER_APP_ID')
pusher_key_id = environ.get('PUSHER_KEY')
pusher_secret = environ.get('PUSHER_SECRET')
pusher_cluster = environ.get('PUSHER_CLUSTER')
pusher_client = pusher.Pusher(app_id=pusher_app_id, key=pusher_key_id, secret=pusher_secret, cluster=pusher_cluster)

# AWS ENV variables
AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY')
MEDIA_BUCKET = environ.get('MEDIA_BUCKET')
S3_RAW_UPLOAD_BUCKET = 'caressa-upload'
S3_BUCKET = s3_bucket_name
S3_REGION = 'https://s3-us-west-1.amazonaws.com'

admin.site.empty_value_display = '-empty-'

WEB_CLIENT = {
    'id': environ.get('WEB_CLIENT_ID', ''),
    'secret': environ.get('WEB_CLIENT_SECRET', ''),
}

PHONENUMBER_DB_FORMAT = 'NATIONAL'
PHONENUMBER_DEFAULT_REGION = 'US'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = environ.get('EMAIL_HOST')
EMAIL_PORT = environ.get('EMAIL_PORT', '587')
EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = environ.get('EMAIL_TLS', True)
EMAIL_USE_SSL = environ.get('EMAIL_USE_SSL', False)

TWILIO_ACCOUNT_SID = environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = environ.get('TWILIO_PHONE_NUMBER')

GOOGLE_APPLICATION_CREDENTIALS_RAW = environ.get('GOOGLE_APPLICATION_CREDENTIALS_RAW')

DATETIME_FORMATS = {
    'spoken': {
        'time': "%I:%M %p"  # e.g. '06:30 PM'
    }
}

SENTRY_DSN = environ.get('SENTRY_DSN')

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()]
)

OPEN_WEATHER_API_KEY = environ.get('OPEN_WEATHER_API_KEY')
