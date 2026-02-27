import platform
from pathlib import Path


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


def get_beat_schedule_filename():
    return Path('tmp') / 'celerybeat-schedule'
