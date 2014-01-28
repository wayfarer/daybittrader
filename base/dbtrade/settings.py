import os

#: System settings

ROOT_DIR = os.path.dirname(os.path.realpath(os.path.dirname(__file__)))
CONFIG_ROOT_DIR = os.path.realpath(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DEFAULT_DB_USER = 'dbtrade'
DEFAULT_DB_PASSWORD = 'orange123'
DEFAULT_DB_HOST = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dbtrade',
        'USER': DEFAULT_DB_USER,
        'PASSWORD': DEFAULT_DB_PASSWORD,
        'HOST': DEFAULT_DB_HOST,
        'PORT': '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Etc/UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '8a#$-)l)6p*uu+neb-v-zl1@4#mqh&amp;^7yym*@3fqdfuvv8gn6w'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request"
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dbtrade.utils.utils.GlobalRequestMiddleware',
)

ROOT_URLCONF = 'dbtrade.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'dbtrade.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(CONFIG_ROOT_DIR, 'templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'south',
    'djcelery',
    'bootstrapform',
    
    'dbtrade.apps.trader'
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

LOGIN_URL = '/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'dbt-maincache',
    }
}

#: celery
import djcelery
djcelery.setup_loader()

BROKER_URL = "redis://adminuser:EgBKtBrtMuoDamKLodGLevLPqfy3JBn7wcAkuMGvCryLLaHJNj@127.0.0.1:6379/0"

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_AUTH = 'EgBKtBrtMuoDamKLodGLevLPqfy3JBn7wcAkuMGvCryLLaHJNj'

CELERYD_MAX_TASKS_PER_CHILD = 100
CELERY_ACKS_LATE = True
CELERYD_PREFETCH_MULTIPLIER = 1

#: App settings

#: First pk in TickerHistory with CB data

CB_STARTING_ID = 37602

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
#EMAIL_HOST_USER = 'notifications@daybittrader.com'
EMAIL_HOST_USER = 'dbtnotifications@gmail.com'
EMAIL_HOST_PASSWORD = 'kzQbED8HV6SC6wEHFK8R'
EMAIL_USE_TLS = True

COINBASE_ID = os.environ.get('DBT_CB_ID', None)
COINBASE_SECRET = os.environ.get('DBT_CB_SECRET', None)
COINBASE_CALLBACK_URL = 'https://daybittrader.com/connect/coinbase/callback/'

BS_PUSHER_APP_ID = 'de504dc5763aeef9ff52'


#: DO NOT EDIT BELOW THIS LINE!!
#: ====================================================

CONFIG = os.environ.get('DBT_SETTINGS_CONFIG', 'debug')

config_module = "dbtrade.config"

# import overrides
overrides = __import__(
    "config." + CONFIG,
    globals(),
    locals(),
    [config_module]
    )

for attr in dir(overrides):
    if attr.isupper():
        globals()[attr] = getattr(overrides, attr)
        
DATABASES['default']['USER'] = DEFAULT_DB_USER
DATABASES['default']['PASSWORD'] = DEFAULT_DB_PASSWORD
DATABASES['default']['HOST'] = DEFAULT_DB_HOST
