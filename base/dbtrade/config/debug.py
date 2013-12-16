DEBUG = True
TEMPLATE_DEBUG = DEBUG

DEFAULT_DB_USER = 'dbtrade'
DEFAULT_DB_PASSWORD = 'orange123'
DEFAULT_DB_HOST = ''

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}