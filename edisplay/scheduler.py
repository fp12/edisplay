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


scheduler.autodiscover_tasks([
    'edisplay.workflows.common',
    'edisplay.workflows.weekday',
    'edisplay.workflows.weekend',
])


scheduler.conf.beat_schedule = {
    # clear caches once a week
    'weekly_0300': {
        'task': 'edisplay.workflows.common.routine_cleaning',
        'schedule': crontab(day_of_week=1, hour=3, minute=0), # Every Monday at 3:00
    },

    # caching things once during the night
    'nightly_0400': {
        'task': 'edisplay.workflows.common.routine_caching',
        'schedule': crontab(hour=4, minute=0), # 4:00
    },

    # background updates
    'weekday_background': {
        'task': 'edisplay.workflows.common.routine_update_device_presence',
        'schedule':  crontab(day_of_week='mon-fri', hour='6-23', minute='*'), # Mon-Fri 6:00 to 23:59 (every minute)
    },
    'weekend_background': {
        'task': 'edisplay.workflows.common.routine_update_device_presence',
        'schedule':  crontab(day_of_week='sat-sun', hour='8-22', minute='*'), # Sat-Sun 8:00 to 22:59 (every minute)
    },

    # 1st early bird
    'weekday_0600_659': {
        'task': 'edisplay.workflows.weekday.routine_0600_0659',
        'schedule':  crontab(day_of_week='mon-thu', hour='6', minute='*'), # Mon-Thu 6:00 to 6:59 (every minute)
    },

    # 2nd early bird
    'weekday_0700_0729': {
        'task': 'edisplay.workflows.weekday.routine_0700_0729',
        'schedule':  crontab(day_of_week='mon-fri', hour='7', minute='0-29'), # Mon-Fri 7:00 to 7:29 (every minute)
    },

    # late bloomers
    'weekday_0730_0759': {
        'task': 'edisplay.workflows.weekday.routine_0730_0829',
        'schedule':  crontab(day_of_week='mon-fri', hour='7', minute='30-59'), # Mon-Fri 7:30 to 7:59 (every minute)
    },
    'weekday_0800_0829': {
        'task': 'edisplay.workflows.weekday.routine_0730_0829',
        'schedule':  crontab(day_of_week='mon-fri', hour='8', minute='0-29'), # Mon-Fri 8:00 to 8:29 (every minute)
    },

    'weekday_0900_2300': {
        'task': 'edisplay.workflows.weekday.routine_0830_2300',
        'schedule':  crontab(day_of_week='mon-fri', hour='9-23', minute='*'), # Mon-Fri 9:00 to 23:59 (every hour)
    },

    'sleep_0000' : {
        'task': 'edisplay.workflows.common.routine_sleep_display',
        'schedule': crontab(hour=0, minute=0), # midnight
    }
}
