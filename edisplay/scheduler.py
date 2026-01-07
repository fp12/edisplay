import os
import platform

from celery import Celery
from celery.schedules import crontab


def get_broker():
    os_name = platform.system()
    if os_name == 'Windows':
        return 'amqp://guest:guest@localhost:5672//'
    elif os_name == 'Linux':
        return 'redis://localhost:6379/0'


def get_backend():
    os_name = platform.system()
    if os_name == 'Windows':
        results_dir = os.path.join('tmp', 'celery_results')
        return f'file://{results_dir}'
    elif os_name == 'Linux':
        return 'redis://localhost:6379/0'


scheduler = Celery('scheduler', broker=get_broker(), backend=get_backend())

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
    'weekday_600_659_routine': {
        'task': 'workflows.weekday_0600_0730_routine',
        'schedule':  crontab(hour='6', minute='*'), # 6:00 AM to 6:59 AM (every minute)
    },
    'weekday_700_730_routine': {
        'task': 'workflows.weekday_0600_0730_routine',
        'schedule':  crontab(hour='7', minute='0-30'), # 7:00 AM to 7:30 AM (every minute)
    }
}
