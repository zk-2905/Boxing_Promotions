from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
import redis

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('mysite')

app.conf.enable_utc = False
app.conf.update(
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0',
    result_backend = 'django-db',
    accept_content = ['application/json'],
    result_serializer =  'json',
    task_serializer = 'json',
    timezone = 'Europe/London',
    )


app.config_from_object(settings, namespace='CELERY')

app.conf.broker_connection_retry_on_startup = True

### Celery Beat ###

app.conf.beat_schedule = {
    'create-events-task': {
        'task': 'box.tasks.create_events',
        'schedule': crontab(minute=0, hour=0, day_of_week='monday'),
    },
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

