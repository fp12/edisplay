from datetime import datetime
from pathlib import Path
from string import Template

from babel.dates import format_date
from celery import shared_task

from edisplay.nba_results import get_games
from edisplay.nba_image import generate_nba_image
from edisplay.image_config import NBA_PANEL_SIZE
from edisplay.tasks.utils import clear_cached_images, fetch_cached_image


@shared_task
def cache_nba_results(date_from, date_to):
    date_from = format_date(date_from, format='yyyy-MM-dd') if isinstance(date_from, datetime) else date_from
    date_to = format_date(date_to, format='yyyy-MM-dd') if isinstance(date_to, datetime) else date_to
    im_path = Path('tmp') / f'nba_results_{date_to}.png'
    if not im_path.exists():
        games = get_games(date_from, date_to)
        im = generate_nba_image(games, NBA_PANEL_SIZE)
        im.save(im_path)


@shared_task
def clear_cached_nba_results():
    clear_cached_images('nba_results_*.png')


@shared_task
def fetch_nba_results_img(date):
    if im := fetch_cached_image(Template('nba_results_$date.png'), date):
        return {'nba': im}
    return {}
