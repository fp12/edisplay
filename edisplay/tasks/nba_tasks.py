import os
import json
from datetime import datetime

from babel.dates import format_date

from edisplay.scheduler import scheduler
from edisplay.nba_results import get_games
from edisplay.nba_image import generate_nba_image


CACHED_GAMES = os.path.join('tmp', 'nba_results.json')


@scheduler.task(name='tasks.cache_nba_results')
def cache_nba_results(date_from, date_to):
    with open(CACHED_GAMES, mode='r+') as f:
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


@scheduler.task(name='tasks.clear_cached_nba_results')
def clear_cached_nba_results():
    with open(CACHED_GAMES, 'w') as f:
        json.dump({}, f)


@scheduler.task(name='tasks.generate_nba_results_img')
def generate_nba_results_img(date_to, size):
    with open(CACHED_GAMES, mode='r') as f:
        results = json.load(f)
        date_to = format_date(date_to, format='yyyy-MM-dd') if isinstance(date_to, datetime) else date_to
        games = results.get(date_to, [])
        return {'nba': generate_nba_image(games, size)}
