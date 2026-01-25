from datetime import datetime, timedelta

from celery import chain, shared_task

from edisplay.tasks.network import update_device_presence 
from edisplay.tasks.nba import cache_nba_results, clear_cached_nba_results
from edisplay.tasks.library import cache_library_info, clear_cached_library_info
from edisplay.tasks.calendar import cache_events, clear_cached_events
from edisplay.tasks.image import sleep_display
from edisplay.tasks.monitoring import dump_health_data


@shared_task
def routine_caching():
    now = datetime.now()
    date_from = now - timedelta(days=3) if now.weekday == 0 else now - timedelta(days=1)
    date_to = now

    job = chain(
        cache_nba_results.si(date_from, date_to),
        cache_library_info.si(),
        cache_events.si(),
    )
    return job.apply_async()


@shared_task
def routine_cleaning():
    job = chain(
        clear_cached_nba_results.si(),
        clear_cached_library_info.si(),
        clear_cached_events.si(),
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


@shared_task
def monitor_performance():
    job = chain(
        dump_health_data.si()
    )
    return job.apply_async()
