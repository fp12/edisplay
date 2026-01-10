from datetime import datetime

from babel.dates import format_date, format_time
from PIL import Image, ImageDraw, ImageText, ImageShow

from edisplay.image_config import WHITE, BLACK, IMG_MODE, WIDTH, PADDING_DEFAULT
from edisplay.fonts import Fira, Quicksand
from edisplay.scheduler import scheduler


@scheduler.task
def generate_date_img(size):
    im = Image.new(IMG_MODE, size, WHITE)
    d = ImageDraw.Draw(im, IMG_MODE)

    now = datetime.now()
    formatted_date = format_date(now, format="EEEE d MMMM", locale='fr_FR')

    text = ImageText.Text(formatted_date, Quicksand.LIGHT.size(28))
    x = (WIDTH - text.get_length()) / 2.0
    y = PADDING_DEFAULT
    d.text((x, y), text, BLACK)

    return {'datetime': im}


@scheduler.task
def generate_datetime_img(size):
    im = Image.new(IMG_MODE, size, WHITE)
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
    result = generate_date_img((460, 150))
    ImageShow.show(result['datetime'])

    result = generate_datetime_img((460, 150))
    ImageShow.show(result['datetime'])
