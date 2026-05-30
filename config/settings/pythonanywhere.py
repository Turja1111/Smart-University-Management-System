"""PythonAnywhere deployment settings.

Use this settings module for PythonAnywhere web apps:
DJANGO_SETTINGS_MODULE=config.settings.pythonanywhere
"""
import os

import dj_database_url
from decouple import config

from .production import *


DEBUG = False

_username = config('PYTHONANYWHERE_USERNAME', default=os.environ.get('USER', '')).strip()
_domain = config('PYTHONANYWHERE_DOMAIN', default='').strip()

_default_hosts = []
if _username:
    _default_hosts.append(f'{_username}.pythonanywhere.com')
if _domain:
    _default_hosts.append(_domain)

_configured_hosts = config('ALLOWED_HOSTS', default=','.join(_default_hosts)).split(',')
ALLOWED_HOSTS = [host.strip() for host in _configured_hosts if host.strip()]

_default_csrf_origins = [f'https://{host}' for host in ALLOWED_HOSTS]
_configured_csrf = config('CSRF_TRUSTED_ORIGINS', default=','.join(_default_csrf_origins)).split(',')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in _configured_csrf if origin.strip()]


# PythonAnywhere free accounts do not include PostgreSQL. Prefer DATABASE_URL
# when available; otherwise use a persistent SQLite file in the project folder.
_db_url = config('DATABASE_URL', default='').strip()
if _db_url:
    DATABASES = {
        'default': dj_database_url.parse(
            _db_url,
            conn_max_age=config('DB_CONN_MAX_AGE', default=600, cast=int),
        ),
    }
elif config('DB_NAME', default='').strip():
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER', default=config('PGUSER', default='')),
            'PASSWORD': config('DB_PASSWORD', default=config('PGPASSWORD', default='')),
            'HOST': config('DB_HOST', default=config('PGHOST', default='localhost')),
            'PORT': config('DB_PORT', default=config('PGPORT', default='5432')),
            'CONN_MAX_AGE': config('DB_CONN_MAX_AGE', default=600, cast=int),
            'OPTIONS': {
                'connect_timeout': config('DB_CONNECT_TIMEOUT', default=10, cast=int),
            },
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        },
    }


# PythonAnywhere serves static/media files directly from Web-tab mappings.
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Free PythonAnywhere accounts do not provide Redis. Keep Celery work inline
# unless you explicitly configure REDIS_URL on a paid account.
if not config('REDIS_URL', default=''):
    CELERY_TASK_ALWAYS_EAGER = True
