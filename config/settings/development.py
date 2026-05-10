"""Development settings"""
from .base import *

DEBUG = True

# Use console email in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery: run tasks eagerly (synchronously) if no Redis
CELERY_TASK_ALWAYS_EAGER = True

# Relaxed throttling for development
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '1000/hour',
    'user': '10000/hour',
    'login': '100/minute',
}

CORS_ALLOW_ALL_ORIGINS = True
