from celery import Celery

from edisplay.scheduler_config import get_broker, get_backend


scheduler_gpio = Celery('scheduler', broker=get_broker(), backend=get_backend())

scheduler_gpio.conf.update(
    task_serializer='pickle',
    accept_content=['pickle', 'json'],
    result_serializer='pickle',
    timezone='America/Montreal',
    enable_utc=True,
    result_expires = 60*10,
)

# Only autodiscover GPIO tasks
scheduler_gpio.autodiscover_tasks(['edisplay.tasks.image'])