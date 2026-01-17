from datetime import datetime, timedelta

from celery import chain, shared_task

from edisplay.tasks.network import update_device_presence 
from edisplay.tasks.nba import cache_nba_results, clear_cached_nba_results
from edisplay.tasks.library import cache_library_info, clear_cached_library_info
from edisplay.tasks.image import sleep_display


@shared_task
def routine_caching():
    """ Caching """
    now = datetime.now()
    date_from = now - timedelta(days=3) if now.weekday == 0 else now - timedelta(days=1)
    date_to = now

    job = chain(
        cache_nba_results.si(date_from, date_to),
        cache_library_info.si(),
    )
    return job.apply_async()


@shared_task
def routine_cleaning():
    """ Cleanup """
    job = chain(
        clear_cached_nba_results.si(),
        clear_cached_library_info.si(),
    )
    return job.apply_async()


@shared_task
def routine_update_device_presence():
    job = chain(
        update_device_presence.si().set(countdown=30),
    )
    return job.apply_async()


@shared_task
def routine_sleep_display():
    job = chain(
        sleep_display.si(),
    )
    return job.apply_async()
