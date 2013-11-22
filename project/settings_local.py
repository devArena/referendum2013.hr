# Django settings for project project.

import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'facebook_example_test_db.sqlite3', # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

FACEBOOK_APP_SECRET = '-- DEFINE IN settings_secret.py --'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# Taken from http://stackoverflow.com/questions/4664724/distributing-django-projects-with-unique-secret-keys
try:
    from secret_key import *
except ImportError:
    SETTINGS_DIR=os.path.abspath(os.path.dirname(__file__))
    def generate_secret_key(file_name):
        import string
        from django.utils.crypto import get_random_string
        f = open(file_name, 'w')
        key = 'SECRET_KEY = "{}"\n'.format(get_random_string(100, string.ascii_letters))
        f.write(key)
        f.close()
    generate_secret_key(os.path.join(SETTINGS_DIR, 'secret_key.py'))
    from secret_key import *

try:
    from settings_secret import *
except ImportError:
    print('ERROR: Secret settings not loaded!')
