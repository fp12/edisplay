from datetime import datetime, timedelta
from pathlib import Path
from string import Template

from babel.dates import format_date
from celery import shared_task
from PIL import Image, ImageOps, ImageText, ImageDraw
from requests.exceptions import ReadTimeout

from edisplay.image_config import NBA_PANEL_SIZE, WHITE, BLACK, IMG_MODE
from edisplay.tasks.utils import clear_cached_images, fetch_cached_image
from edisplay.fonts import Fira


NBA_LOGO = Path('img') / 'nba' / 'nba-logo-bw.jpg'
COLUMNS = 2
LINES = 4
MAX_GAMES = COLUMNS * LINES


def generate_nba_image(games):
    size = NBA_PANEL_SIZE
    with Image.open(NBA_LOGO) as im:
        im = im.convert(IMG_MODE)
        ratio = im.width / im.height
        im = ImageOps.pad(im, size, color=WHITE, centering=(0.0, 0.5))
        d = ImageDraw.Draw(im, IMG_MODE)

        initial_x = size[1] * ratio

        if games:
            for index, game in enumerate(games[:MAX_GAMES]):
                text = ImageText.Text(game, Fira.SEMIBOLD.size(18))
                text_width = text.get_bbox()[2]
                total_width = COLUMNS * text_width
                x_padding = (size[0] - total_width - initial_x) / (COLUMNS + 1)
                x = initial_x + x_padding
                if index > LINES - 1:
                    x += text_width + x_padding

                text_height = text.get_bbox()[3]
                total_height = text_height * LINES
                y_padding = (size[1] - total_height) / (LINES + 1)
                y = y_padding + (index % LINES) * (text_height + y_padding)
                d.text((x, y), text, BLACK)
        else:
            text = ImageText.Text('No Games', Fira.SEMIBOLD.size(25))
            x = initial_x + 20
            y = size[1] / 2
            d.text((x, y), text, BLACK)
        
        return im


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def cache_nba_results(self):
    now = datetime.now()
    yesterday = now - timedelta(days=1)

    formatted_yesterday = format_date(yesterday, format='yyyy-MM-dd')
    im_path = Path('tmp') / f'nba_results_{formatted_yesterday}.png'
    if not im_path.exists():
        try:
            from edisplay.nba import get_results
            games = get_results(yesterday, now)
            im = generate_nba_image(games)
            im.save(im_path)
        except ReadTimeout as exc:
            raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def cache_nba_games(self):
    now = datetime.now()

    formatted_now = format_date(now, format='yyyy-MM-dd')
    im_path = Path('tmp') / f'nba_games_{formatted_now}.png'
    if not im_path.exists():
        try:
            from edisplay.nba import get_games
            games = get_games(now)
            im = generate_nba_image(games)
            im.save(im_path)
        except ReadTimeout as exc:
            raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)


@shared_task
def clear_cached_nba_img():
    clear_cached_images('nba_results_*.png')
    clear_cached_images('nba_games_*.png')


@shared_task
def fetch_nba_results_img(date):
    if im := fetch_cached_image(Template('nba_results_$date.png'), date):
        return {'nba': im}
    return {}


@shared_task
def fetch_nba_games_img(date):
    if im := fetch_cached_image(Template('nba_games_$date.png'), date):
        return {'nba': im}
    return {}
