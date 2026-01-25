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
from edisplay.tasks.message import generate_message_img


@shared_task
def routine_0600_0659():
    now = datetime.now()

    if is_device_connected('id1'):
        job = chain(
            group(
                generate_time_img.s(),
                fetch_events_img.s(now),
                generate_stm_img.s(['45N']),
                generate_meteo_img.s(now, now),
                fetch_library_info_img.s()
            ),
            assemble_img.s(),
            publish_img.s()
        )
        return job.apply_async()


@shared_task
def routine_0700_0729():
    now = datetime.now()

    if is_device_connected('id2'):
        id1_updated = has_device_status_changed_recently('id1')
        bus_stops = ['45N', '47E', '197E'] if is_device_connected('id1') else ['47E', '197E']
        job = chain(
            group(
                generate_datetime_img.s(),
                generate_stm_img.s(bus_stops),
                generate_meteo_img.s(now, now),
                fetch_nba_results_img.s(now),
            ),
            assemble_img.s(),
            publish_img.s()
        )
        return job.apply_async(full_refresh=id1_updated)


@shared_task
def routine_0730_0829():
    now = datetime.now()

    id1_updated = has_device_status_changed_recently('id1')

    job = chain(
        group(
            generate_datetime_img.s(),
            generate_message_img.s('weekday_morning'),
            fetch_events_img.s(now),
            generate_meteo_img.s(now, now),
            fetch_nba_results_img.s(now),
        ),
        assemble_img.s(),
        publish_img.s(full_refresh=id1_updated)
    )
    return job.apply_async()


@shared_task
def routine_0830_2300():
    id0_updated = has_device_status_changed_recently('id0')
    id1_updated = has_device_status_changed_recently('id1')
    id2_updated = has_device_status_changed_recently('id2')

    if are_devices_connected(['id0', 'id1', 'id2'], any):
        now = datetime.now()

        day_group = group(
            generate_time_img.s(),
            fetch_events_img.s(now),
            generate_message_img.s('evening'),
            fetch_nba_results_img.s(now),
            # nba upcoming games
        )

        if is_device_connected('id1'):
            day_group = group(
                generate_time_img.s(),
                fetch_events_img.s(now),
                generate_message_img.s('evening'),
                generate_meteo_img.s(now, now),
                fetch_library_info_img.s(),
                fetch_nba_results_img.s(now),
                # nba upcoming games
            )
        
        job = chain(
            day_group,
            assemble_img.s(),
            publish_img.s(full_refresh=id1_updated or id2_updated)
        )
        return job.apply_async()
    else:
        print('no device connected: getting into sleep mode')

        if any([id0_updated, id1_updated, id2_updated]):
            job = chain(
                sleep_display.s()
            )
            return job.apply_async()
