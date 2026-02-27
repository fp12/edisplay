from datetime import datetime, timedelta

from celery import shared_task, chain

from edisplay.tasks.utils import independant_chain
from edisplay.tasks.network import update_device_presence 
from edisplay.tasks.nba import cache_nba_results, clear_cached_nba_img, cache_nba_games
from edisplay.tasks.library import cache_library_info, clear_cached_library_info
from edisplay.tasks.calendar import cache_events, clear_cached_events
from edisplay.tasks.image import sleep_display, assemble_img, publish_img
from edisplay.tasks.monitoring import dump_health_data
from edisplay.tasks.message import generate_boot_img


@shared_task
def routine_booting():
    job = chain(
        generate_boot_img.s(),
        assemble_img.s(),
        publish_img.s()
    )
    return job.apply_async()


@shared_task
def routine_caching():
    job = independant_chain([
        cache_nba_results.si(),
        cache_nba_games.si(),
        cache_library_info.si(),
        cache_events.si(),
    ])
    return job.apply_async()


@shared_task
def routine_cleaning():
    job = independant_chain([
        clear_cached_nba_img.si(),
        clear_cached_library_info.si(),
        clear_cached_events.si(),
    ])
    return job.apply_async()


@shared_task(bind=True)
def routine_update_device_presence(self):
    return update_device_presence.si().set(countdown=30).apply_async()


@shared_task
def routine_sleep_display():
    return sleep_display.si().apply_async()


@shared_task
def monitor_performance():
    return dump_health_data.si().apply_async()
