from __future__ import absolute_import, unicode_literals
from celery.schedules import crontab
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE','instagram_api.settings')

app = Celery('instagram_api')
app.conf.beat_schedule = {
    'delete-old-posts-every-day': {
        'task': 'post_app.tasks.permanently_delete_posts',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
}

app.config_from_object('django.conf:settings',namespace= 'CELERY')
app.autodiscover_tasks(['user'])