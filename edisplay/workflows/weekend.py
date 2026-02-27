from datetime import datetime, timedelta

from celery import chain, group, shared_task

from edisplay.tasks.time import generate_date_img, generate_datetime_img, generate_time_img
from edisplay.tasks.calendar import fetch_events_img
from edisplay.tasks.meteo import generate_meteo_img
from edisplay.tasks.nba import fetch_nba_results_img, fetch_nba_games_img
from edisplay.tasks.library import fetch_library_info_img
from edisplay.tasks.stm import generate_stm_img
from edisplay.tasks.image import assemble_img, publish_img, sleep_display
from edisplay.tasks.network import is_device_connected, are_devices_connected, has_device_status_changed_recently, get_devices_presence


@shared_task
def routine_saturday(**kwargs):
    devices = get_devices_presence(['id0', 'id1', 'id2'])

    if devices.any_connected():
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        tasks = [generate_time_img.s()]

        if kwargs.get('events_today'):
            tasks.append(fetch_events_img.s(now))
        
        if kwargs.get('events_tomorrow'):
            tasks.append(fetch_events_img.s(tomorrow))
            
        tasks.append(generate_meteo_img.s(now, now))

        if bus_stops := kwargs.get('bus_stops'):
            tasks.append(generate_stm_img.s(bus_stops))

        if devices.is_any_connected(['id0', 'id2']):
            if kwargs.get('nba_results'):
                tasks.append(fetch_nba_results_img.s(yesterday))
            
            if kwargs.get('nba_games'):
                tasks.append(fetch_nba_games_img.s(now))

        job = chain(
            group(tasks),
            assemble_img.s(),
            publish_img.s(full_refresh=devices.any_changed())
        )
        return job.apply_async()
    else:
        if devices.any_changed():
            print('no device connected: getting into sleep mode')
            job = sleep_display.s()
            return job.apply_async()

@shared_task
def routine_sunday(**kwargs):
    devices = get_devices_presence(['id0', 'id1', 'id2'])

    if devices.any_connected():
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        tasks = [generate_time_img.s()]

        if kwargs.get('events_today'):
            tasks.append(fetch_events_img.s(now))
        
        if kwargs.get('events_tomorrow'):
            tasks.append(fetch_events_img.s(tomorrow))

        tasks.append(generate_meteo_img.s(now, now))

        if devices.is_any_connected(['id0', 'id2']):
            if kwargs.get('nba_results'):
                tasks.append(fetch_nba_results_img.s(yesterday))
            
            if kwargs.get('nba_games'):
                tasks.append(fetch_nba_games_img.s(now))

        job = chain(
            group(tasks),
            assemble_img.s(),
            publish_img.s(full_refresh=devices.any_changed())
        )
        return job.apply_async()

    else:
        if devices.any_changed():
            print('no device connected: getting into sleep mode')
            job = sleep_display.s()
            return job.apply_async()
