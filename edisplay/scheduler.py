import os

from celery import Celery
from celery.schedules import crontab

RESULTS_DIR = os.path.join('tmp', 'celery_results')

scheduler = Celery('scheduler', broker='amqp://guest:guest@localhost:5672//', backend=f'file://{RESULTS_DIR}')

scheduler.conf.update(
    task_serializer='pickle',
    accept_content=['pickle', 'json'],
    result_serializer='pickle',
    timezone='America/Montreal',
    enable_utc=True,
    beat_schedule_filename=os.path.join('tmp', 'celerybeat-schedule'),
)

scheduler.autodiscover_tasks(['edisplay.tasks', 'edisplay.workflows'])

scheduler.conf.beat_schedule = {
    'nightly_routine': {
        'task': 'workflows.nightly_routine',
        'schedule': crontab(hour=4, minute=0),
    },
    'weekday_morning_routine': {
        'task': 'workflows.weekday_morning_routine',
        'schedule': 5.0
    }
}
