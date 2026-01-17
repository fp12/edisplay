from datetime import datetime

from babel.dates import format_date
from celery import shared_task

from edisplay.meteo_image import generate_image as generate_meteo_img_impl
from edisplay.image_config import METEO_PANEL_SIZE


@shared_task
def generate_meteo_img(date_from, date_to):
    date_from = format_date(date_from, format='yyyy-MM-dd') if isinstance(date_from, datetime) else date_from
    date_to = format_date(date_to, format='yyyy-MM-dd') if isinstance(date_to, datetime) else date_to
    try:
        return {'meteo': generate_meteo_img_impl(date_from, date_to, METEO_PANEL_SIZE)}
    except Exception as e:
        print(f'`generate_meteo_img` raised an exception but it was handled: {e}')
        return {f'error-meteo': e}
