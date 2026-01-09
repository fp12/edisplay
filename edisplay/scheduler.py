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
    # caching things once during the night
    'nightly': {
        'task': 'workflows.nightly_routine',
        'schedule': crontab(hour=4, minute=0), # 4:00
    },

    # 1st early bird
    'weekday_600_659': {
        'task': 'workflows.weekday_0600_0659_routine',
        'schedule':  crontab(hour='6', minute='*'), # 6:00 to 6:59 (every minute)
    },

    # 2nd early bird
    'weekday_0700_0729': {
        'task': 'workflows.weekday_0700_0729_routine',
        'schedule':  crontab(hour='7', minute='0-29'), # 7:00 to 7:29 (every minute)
    },

    # late bloomers
    'weekday_0730_0759': {
        'task': 'workflows.weekday_0730_0829_routine',
        'schedule':  crontab(hour='7', minute='30-59'), # 7:30 to 7:59 (every minute)
    },
    'weekday_0800_0829': {
        'task': 'workflows.weekday_0730_0829_routine',
        'schedule':  crontab(hour='8', minute='0-29'), # 8:00 to 8:29 (every minute)
    },

    # rest of the day
    'weekday_0830_0859': {
        'task': 'workflows.weekday_0830_2300_routine',
        'schedule':  crontab(hour='8', minute='30-59'), # 8:30 to 8:59 (every minute)
    },
    'weekday_0900_2359': {
        'task': 'workflows.weekday_0830_2300_routine',
        'schedule':  crontab(hour='9-23', minute='*'), # 9:00 to 23:59 (every minute)
    },

    'sleep_0000' : {
        'task': 'tasks.sleep_display',
        'schedule': crontab(hour=0, minute=0), # midnight
    }
}