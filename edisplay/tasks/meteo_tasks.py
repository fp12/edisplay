from datetime import datetime

from babel.dates import format_date

from edisplay.meteo_image import generate_image as generate_meteo_img_impl
from edisplay.scheduler import scheduler


@scheduler.task(name='tasks.generate_meteo_img')
def generate_meteo_img(date_from, date_to, size):
    date_from = format_date(date_from, format='yyyy-MM-dd') if isinstance(date_from, datetime) else date_from
    date_to = format_date(date_to, format='yyyy-MM-dd') if isinstance(date_to, datetime) else date_to
    return {'meteo': generate_meteo_img_impl(date_from, date_to, size)}
