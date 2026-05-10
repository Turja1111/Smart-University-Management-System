"""
SUMS config package — registers Celery app so shared_task works across all apps.
"""
from .celery import app as celery_app

__all__ = ('celery_app',)
