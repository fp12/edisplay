from celery import Celery
from celery.schedules import crontab

from edisplay.scheduler_config import get_broker, get_backend, get_beat_schedule_filename


scheduler_beat = Celery('scheduler', broker=get_broker(), backend=get_backend())
scheduler_beat.conf.update(
    task_serializer='pickle',
    accept_content=['pickle', 'json'],
    result_serializer='pickle',
    timezone='America/Montreal',
    enable_utc=True,
    result_expires = 60*10,
    beat_schedule_filename=get_beat_schedule_filename(),
)


scheduler_beat.conf.beat_schedule = {
    # clear caches once a week
    'weekly_0100': {
        'task': 'edisplay.workflows.common.routine_cleaning',
        'schedule': crontab(day_of_week=1, hour=1, minute=0),
    },

    # caching things once during the night
    'nightly_0400': {
        'task': 'edisplay.workflows.common.routine_caching',
        'schedule': crontab(hour=4, minute=0),
    },

    # getting the display to sleep at midnight
    'sleep_0000' : {
        'task': 'edisplay.workflows.common.routine_sleep_display',
        'schedule': crontab(hour=0, minute=0),
    },

    # background updates
    'weekday_background': {
        'task': 'edisplay.workflows.common.routine_update_device_presence',
        'schedule': crontab(day_of_week='mon-fri', hour='6-23', minute='*/2'),
    },
    'weekend_background': {
        'task': 'edisplay.workflows.common.routine_update_device_presence',
        'schedule': crontab(day_of_week='sat-sun', hour='8-22', minute='*/2'),
    },
    'monitoring': {
        'task': 'edisplay.workflows.common.monitor_performance',
        'schedule': crontab(minute='*/5'),
    },

    # 1st early bird
    'weekday_0600_0659': {
        'task': 'edisplay.workflows.weekday.routine_0600_0659',
        'schedule': crontab(day_of_week='mon-thu', hour='6', minute='*'),
    },

    # 2nd early bird
    'weekday_0700_0729': {
        'task': 'edisplay.workflows.weekday.routine_0700_0729',
        'schedule': crontab(day_of_week='mon-fri', hour='7', minute='0-29'),
    },

    # late bloomers
    'weekday_0730_0759': {
        'task': 'edisplay.workflows.weekday.routine_0730_0829',
        'schedule': crontab(day_of_week='mon-fri', hour='7', minute='30-59'),
    },
    'weekday_0800_0829': {
        'task': 'edisplay.workflows.weekday.routine_0730_0829',
        'schedule': crontab(day_of_week='mon-fri', hour='8', minute='0-29'),
    },
    'weekday_0830': {
        'task': 'edisplay.workflows.weekday.routine_0830',
        'schedule': crontab(day_of_week='mon-fri', hour='8', minute='30'),
    },
    'weekday_0831_0859': {
        'task': 'edisplay.workflows.weekday.routine_0831_2300',
        'schedule': crontab(day_of_week='mon-fri', hour='8', minute='31-59'),
    },

    # most of the week afternoon / evening
    'weekday_0900_2359': {
        'task': 'edisplay.workflows.weekday.routine_0831_2300',
        'schedule': crontab(day_of_week='mon,wed,thu,fri', hour='9-23', minute='*'),
    },
    # tuesday special
    'tuesday_0900_1859': {
        'task': 'edisplay.workflows.weekday.routine_0831_2300',
        'schedule': crontab(day_of_week='tue', hour='9-18', minute='*'),
    },
    'tuesday_1900_1959': {
        'task': 'edisplay.workflows.weekday.routine_tuesday_1900_1959',
        'schedule': crontab(day_of_week='tue', hour='19', minute='*'),
    },
    'tuesday_2000_2359': {
        'task': 'edisplay.workflows.weekday.routine_0831_2300',
        'schedule': crontab(day_of_week='tue', hour='20-23', minute='*'),
    },

    # saturday
    'saturday_0900_1559': {
        'task': 'edisplay.workflows.weekend.routine_saturday',
        'kwargs': {'nba_results': True, 'wnba_results': True},
        'schedule': crontab(day_of_week='sat', hour='9-15', minute='*'),
    },
    'saturday_1600_1659': {
        'task': 'edisplay.workflows.weekend.routine_saturday',
        'kwargs': {'bus_stops': ['45N'], 'nba_games': True},
        'schedule': crontab(day_of_week='sat', hour='16', minute='*'),
    },
    'saturday_1700_2359': {
        'task': 'edisplay.workflows.weekend.routine_saturday',
        'kwargs': {'events_tomorrow': True, 'nba_games': True},
        'schedule': crontab(day_of_week='sat', hour='17-23', minute='*'),
    },

    # sunday
    'sunday_0900_1659': {
        'task': 'edisplay.workflows.weekend.routine_sunday',
        'kwargs': {'events_today': True, 'nba_results': True, 'wnba_results': True},
        'schedule': crontab(day_of_week='sun', hour='9-16', minute='*'),
    },
    'sunday_1700_2359': {
        'task': 'edisplay.workflows.weekend.routine_sunday',
        'kwargs': {'events_tomorrow': True, 'nba_games': True},
        'schedule': crontab(day_of_week='sun', hour='17-23', minute='*'),
    },
}