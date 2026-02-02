from functools import wraps
from pathlib import Path
from datetime import datetime

from babel.dates import format_date
from PIL import Image


def independant_chain(tasks):
    # Iterate backwards to link each task to its successor
    next_task = None
    for task in reversed(tasks):
        if next_task:
            # Trigger 'next_task' on both success and failure
            task.set(link=next_task, link_error=next_task)
        next_task = task
    return next_task


def auto_handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f'{func.__name__} raised an exception but it was handled {e}')
            return {f'error-{func.__name__}': e}
    return wrapper


def clear_cached_images(pattern):
    directory_path = Path('tmp')
    for file_path in directory_path.glob(pattern):
        try:
            if file_path.is_file():
                file_path.unlink()
                print(f'Deleted: {file_path}')
        except OSError as e:
            print(f'Error deleting {file_path}: {e}')


def fetch_cached_image(template, date):
    date = format_date(date, format='yyyy-MM-dd') if isinstance(date, datetime) else date
    im_file_path = Path('tmp') / template.substitute({'date': date})
    if im_file_path.exists():
        print(f'Loading cached image from {im_file_path}')
        with Image.open(im_file_path) as im:
            im.load()
            # Create a copy so we can close the file safely
            return im.copy()
    print(f'Couldn\'t fetch cached image {im_file_path}')
    return None
