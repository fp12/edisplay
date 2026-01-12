from datetime import datetime, timedelta

from celery import chain

from edisplay.scheduler import scheduler
from edisplay.tasks import cache_nba_results, clear_cached_nba_results, cache_library_info, clear_cached_library_info


@scheduler.task(name='workflows.nightly_routine')
def nightly_routine():
    """ Caching """
    now = datetime.now()
    date_from = now - timedelta(days=3) if now.weekday == 0 else now - timedelta(days=1)
    date_to = now

    job = chain(
        cache_nba_results.si(date_from, date_to),
        cache_library_info.si(),
    )
    return job.apply_async()


@scheduler.task(name='workflows.weekly_routine')
def weekly_routine():
    """ Cleanup """
    job = chain(
        clear_cached_nba_results.si(),
        clear_cached_library_info.si(),
    )
    return job.apply_async()
