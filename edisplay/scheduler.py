import os
import platform

from celery import Celery
from celery.schedules import crontab

from edisplay.scheduler_config import get_broker, get_backend, get_beat_schedule_filename


scheduler = Celery('scheduler', broker=get_broker(), backend=get_backend())

scheduler.conf.update(
    task_serializer='pickle',
    accept_content=['pickle', 'json'],
    result_serializer='pickle',
    timezone='America/Montreal',
    enable_utc=True,
    result_expires = 60*10,  # 10 minutes
    beat_schedule_filename=get_beat_schedule_filename(),
)

scheduler.autodiscover_tasks([
    'edisplay.workflows.common',
    'edisplay.workflows.weekday',
    'edisplay.workflows.weekend',
])
