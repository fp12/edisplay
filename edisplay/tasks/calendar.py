import re
import platform
from pathlib import Path
from datetime import datetime, timezone, timedelta

from PIL import Image, ImageOps, ImageText, ImageDraw, ImageShow
from celery import shared_task
from babel.dates import format_date, format_time

from edisplay.image_config import WHITE, BLACK, IMG_MODE, CALENDAR_PANEL_SIZE
from edisplay.fonts import Quicksand, Fira
from edisplay.calendar import get_events
from edisplay.secrets import get_secret


CALENDAR_ICON = Path('img', 'calendar', 'calendar.png')
INITIALS = ''.join(get_secret('Calendar', 'Participants').keys())
PATTERN = re.compile(rf'{{(?P<participants>[{INITIALS}]+)}} (?P<title>\w+)')
TEXT_FEATURES = ['+liga'] if platform.system() == 'Linux' else None


def parse_summary(summary):
    if m:= PATTERN.match(summary):
        mapping = get_secret('Calendar', 'Participants')
        participants = [mapping[c] for c in m['participants']]
        return participants, m['title']


@shared_task
def cache_events():
    now = datetime.now(tz=timezone.utc)
    tomorrow = now + timedelta(days=1)
    from_date = now.isoformat()
    to_date = tomorrow.isoformat()
    events = get_events(from_date, to_date)

    with Image.open(CALENDAR_ICON) as im:
        im = im.convert(IMG_MODE)
        ratio = im.width / im.height
        im = ImageOps.pad(im, CALENDAR_PANEL_SIZE, color=WHITE, centering=(0.0, 0.5))
        d = ImageDraw.Draw(im, IMG_MODE)

        text = ImageText.Text(str(now.day), Quicksand.BOLD.size(75))
        d.text((8, 15), text, BLACK)
        
        x = CALENDAR_PANEL_SIZE[1] * ratio + 5

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

            date_to = format_date(now, format='yyyy-MM-dd')
            im_file_path = Path('tmp') / f'events_{date_to}.png'
            im.save(im_file_path)

            return im


@shared_task
def clear_cached_events():
    directory_path = Path('tmp')
    pattern = 'events_*.png'
    for file_path in directory_path.glob(pattern):
        try:
            if file_path.is_file():
                file_path.unlink()
                print(f'Deleted: {file_path}')
        except OSError as e:
            print(f'Error deleting {file_path}: {e}')


@shared_task
def fetch_events_img(date):
    date = format_date(date, format='yyyy-MM-dd') if isinstance(date, datetime) else date
    im_file_path = os.path.join('tmp', f'events_{date_to}.png')
    if os.path.exists(im_file_path):
        print(f'Loading cached events image from {im_file_path}')
        return {'calendar': Image.open(im_file_path)}
    print('Couldn\'t fetch cached events image')
    return {}


if __name__ == '__main__':
    if platform.system() == 'Windows':
        ImageShow.show(cache_calendar_info())
