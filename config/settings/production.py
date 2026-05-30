"""Production settings"""
import os

from .base import *
from decouple import config

DEBUG = False

_render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
_railway_hostname = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
_platform_hosts = ','.join(host for host in [_render_hostname, _railway_hostname] if host)

_allowed_hosts = config('ALLOWED_HOSTS', default=_platform_hosts).split(',')
ALLOWED_HOSTS = [host.strip() for host in _allowed_hosts if host.strip()]

for host in [_render_hostname, _railway_hostname]:
    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

_csrf_origins = config('CSRF_TRUSTED_ORIGINS', default='').split(',')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in _csrf_origins if origin.strip()]

for host in [_render_hostname, _railway_hostname]:
    origin = f'https://{host}' if host else ''
    if origin and origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

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
