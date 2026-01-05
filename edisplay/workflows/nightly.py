from datetime import datetime, timedelta

from celery import chain

from edisplay.scheduler import scheduler
from edisplay.tasks import cache_nba_results, clear_cached_nba_results


@scheduler.task(name='workflows.nightly_routine')
def nightly_routine():
    """ Cleanup / Caching as needed"""
    now = datetime.now()
    date_from = now - timedelta(days=3) if now.weekday == 0 else now - timedelta(days=1)
    date_to = now

    job = chain(
        clear_cached_nba_results.si(),
        cache_nba_results.si(date_from, date_to)
    )
    return job.apply_async()
