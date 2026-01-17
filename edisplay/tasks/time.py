from datetime import datetime

from babel.dates import format_date, format_time
from PIL import Image, ImageDraw, ImageText, ImageShow
from celery import shared_task

from edisplay.image_config import WHITE, BLACK, IMG_MODE, WIDTH, PADDING_DEFAULT, DATE_SIZE, DATETIME_SIZE
from edisplay.fonts import Fira, Quicksand


@shared_task
def generate_date_img():
    im = Image.new(IMG_MODE, DATE_SIZE, WHITE)
    d = ImageDraw.Draw(im, IMG_MODE)

    now = datetime.now()
    formatted_date = format_date(now, format="EEEE d MMMM", locale='fr_FR')

    text = ImageText.Text(formatted_date, Quicksand.LIGHT.size(28))
    x = (WIDTH - text.get_length()) / 2.0
    y = PADDING_DEFAULT
    d.text((x, y), text, BLACK)

    return {'datetime': im}


@shared_task
def generate_datetime_img():
    im = Image.new(IMG_MODE, DATETIME_SIZE, WHITE)
    d = ImageDraw.Draw(im, IMG_MODE)

    now = datetime.now()
    formatted_date = format_date(now, format="EEEE d MMMM", locale='fr_FR')
    formatted_time = format_time(now, format="H:mm", locale='fr_FR')

    text = ImageText.Text(formatted_date, Quicksand.LIGHT.size(28))
    x = (WIDTH - text.get_length()) / 2.0
    y = PADDING_DEFAULT
    d.text((x, y), text, BLACK)

    y += text.get_bbox()[3] + PADDING_DEFAULT
    text = ImageText.Text(formatted_time, Fira.RETINA.size(100))
    x = (WIDTH - text.get_length()) / 2.0
    d.text((x, y), text, BLACK)
    y += text.get_bbox()[3] + 50

    return {'datetime': im}


if __name__ == '__main__':
    result = generate_date_img()
    ImageShow.show(result['datetime'])

    result = generate_datetime_img()
    ImageShow.show(result['datetime'])
