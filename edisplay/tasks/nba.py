import os
import json
import logging
from datetime import datetime
from pathlib import Path

from babel.dates import format_date
from PIL import Image
from celery import shared_task

from edisplay.nba_results import get_games
from edisplay.nba_image import generate_nba_image
from edisplay.image_config import NBA_PANEL_SIZE


CACHED_NBA_RESULTS = os.path.join('tmp', 'nba_results.json')
CACHED_NBA_RESULTS_IMG = os.path.join('tmp', 'nba_results.json')


@shared_task
def cache_nba_results(date_from, date_to):
    with open(CACHED_NBA_RESULTS, mode='r+') as f:
        results = json.load(f)
        games = results.get(date_to, [])
        if not games:
            date_from = format_date(date_from, format='yyyy-MM-dd') if isinstance(date_from, datetime) else date_from
            date_to = format_date(date_to, format='yyyy-MM-dd') if isinstance(date_to, datetime) else date_to
            games = get_games(date_from, date_to)
            results[date_to] = games
            f.seek(0)
            f.truncate()
            json.dump(results, f)

            im_file_path = os.path.join('tmp', f'nba_results_{date_to}.png')
            im = generate_nba_image(games, NBA_PANEL_SIZE)
            im.save(im_file_path)


@shared_task
def clear_cached_nba_results():
    with open(CACHED_NBA_RESULTS, 'w') as f:
        json.dump({}, f)

    directory_path = Path('tmp')
    pattern = 'nba_results_*.png'
    for file_path in directory_path.glob(pattern):
        try:
            if file_path.is_file():
                file_path.unlink()
                print(f'Deleted: {file_path}')
        except OSError as e:
            print(f'Error deleting {file_path}: {e}')


@shared_task
def fetch_nba_results_img(date_to):
    date_to = format_date(date_to, format='yyyy-MM-dd') if isinstance(date_to, datetime) else date_to
    im_file_path = os.path.join('tmp', f'nba_results_{date_to}.png')
    if os.path.exists(im_file_path):
        print(f'Loading cached NBA image from {im_file_path}')
        return {'nba': Image.open(im_file_path)}
    print('Couldn\'t fetch cached nba image')
    return {}
