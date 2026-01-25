from datetime import datetime

from celery import chain, group, shared_task

from edisplay.tasks.time import generate_date_img, generate_datetime_img, generate_time_img
from edisplay.tasks.calendar import fetch_events_img
from edisplay.tasks.meteo import generate_meteo_img
from edisplay.tasks.nba import fetch_nba_results_img
from edisplay.tasks.library import fetch_library_info_img
from edisplay.tasks.stm import generate_stm_img
from edisplay.tasks.image import assemble_img, publish_img, sleep_display
from edisplay.tasks.network import is_device_connected, are_devices_connected, has_device_status_changed_recently


@shared_task
def routine_0600_2300():
    now = datetime.now()
    
    job = chain(
        group(
            generate_date_img.s(),
            # generate_meteo_img.s(now, now),
            fetch_nba_results_img.s(now),
        ),
        assemble_img.s(),
        publish_img.s()
    )
    return job.apply_async()


@shared_task
def routine_saturday(**kwargs):
    id0_updated = has_device_status_changed_recently('id0')
    id1_updated = has_device_status_changed_recently('id1')
    id2_updated = has_device_status_changed_recently('id2')

    if are_devices_connected(['id0', 'id1', 'id2'], any):
        now = datetime.now()

        tasks = [
            generate_time_img.s(),
            fetch_events_img.s(now),
            generate_meteo_img.s(now, now),
        ]

        if bus_stops := kwargs.get('bus_stops'):
            tasks.append(generate_stm_img.s(bus_stops))

        if are_devices_connected(['id0', 'id2'], any):
            tasks.append(fetch_nba_results_img.s(now))

        job = chain(
            group(tasks),
            assemble_img.s(),
            publish_img.s()
        )
        return job.apply_async()
    else:
        print('no device connected: getting into sleep mode')

        if any([id0_updated, id1_updated, id2_updated]):
            job = sleep_display.s()
            return job.apply_async()
