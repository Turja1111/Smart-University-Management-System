"""Production settings"""
import os

from .base import *
from decouple import config

DEBUG = False

_render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
_allowed_hosts = config('ALLOWED_HOSTS', default=_render_hostname).split(',')
ALLOWED_HOSTS = [host.strip() for host in _allowed_hosts if host.strip()]

if _render_hostname and _render_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_render_hostname)

_csrf_origins = config('CSRF_TRUSTED_ORIGINS', default='').split(',')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in _csrf_origins if origin.strip()]

if _render_hostname:
    CSRF_TRUSTED_ORIGINS.append(f'https://{_render_hostname}')

if not config('REDIS_URL', default=''):
    CELERY_TASK_ALWAYS_EAGER = True

# Real email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Security
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
