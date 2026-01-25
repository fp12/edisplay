import re
import platform
from pathlib import Path
from datetime import datetime, timezone, timedelta
from string import Template

from PIL import Image, ImageOps, ImageText, ImageDraw, ImageShow
from celery import shared_task
from babel.dates import format_date, format_time

from edisplay.image_config import WHITE, BLACK, IMG_MODE, CALENDAR_PANEL_SIZE
from edisplay.fonts import Quicksand, Fira
from edisplay.calendar import get_events
from edisplay.secrets import get_secret
from edisplay.tasks.utils import clear_cached_images, fetch_cached_image


CALENDAR_ICON = Path('img', 'calendar', 'calendar.png')
INITIALS = ''.join(get_secret('Calendar', 'Participants').keys())
PATTERN = re.compile(rf'{{(?P<participants>[{INITIALS}]+)}} (?P<title>\w+)')
TEXT_FEATURES = ['+liga'] if platform.system() == 'Linux' else None


def parse_summary(summary):
    if m:= PATTERN.match(summary):
        mapping = get_secret('Calendar', 'Participants')
        participants = [mapping[c] for c in m['participants']]
        return participants, m['title']


def generate_events_image(events, date):
    with Image.open(CALENDAR_ICON) as im:
        im = im.convert(IMG_MODE)
        ratio = im.width / im.height
        im = ImageOps.pad(im, CALENDAR_PANEL_SIZE, color=WHITE, centering=(0.0, 0.5))
        d = ImageDraw.Draw(im, IMG_MODE)

        text = ImageText.Text(str(date.day), Quicksand.BOLD.size(75))
        d.text((8, 15), text, BLACK)
        
        x = CALENDAR_PANEL_SIZE[1] * ratio + 7

        events_num = len(events)
        for index, event in enumerate(events):
            participants, title = parse_summary(event.summary)
            start_time = format_time(event.start, format="H:mm", locale='fr_FR')
            text = ImageText.Text(f'▶ {start_time} {title} ({" ".join(participants)})', Fira.RETINA.size(20))

            text_height = text.get_bbox()[3]
            total_height = text_height * events_num
            y_padding = (CALENDAR_PANEL_SIZE[1] - total_height) // (events_num + 1)
            y = y_padding + (text_height + y_padding) * index + 0

            d.text((x, y), text, BLACK, features=TEXT_FEATURES)

        formatted_date = format_date(date, format='yyyy-MM-dd')
        im_file_path = Path('tmp') / f'events_{formatted_date}.png'
        im.save(im_file_path)


@shared_task
def cache_events():
    now = datetime.now(tz=timezone.utc)

    tomorrow = now + timedelta(days=1)
    if events := get_events(now.isoformat(), tomorrow.isoformat()):
        generate_events_image(events, now)
        
    overmorrow = tomorrow + timedelta(days=1)
    if events := get_events(tomorrow.isoformat(), overmorrow.isoformat()):
        generate_events_image(events, now)


@shared_task
def clear_cached_events():
    clear_cached_images('events_*.png')


@shared_task
def fetch_events_img(date):
    if im := fetch_cached_image(Template('events_$date.png'), date):
        return {'calendar': im}
    return {}


if __name__ == '__main__':
    im = cache_events()
    if platform.system() == 'Windows':
        ImageShow.show(im)

