from datetime import datetime

from celery import chain, group

from edisplay.scheduler import scheduler
from edisplay.tasks import (
    generate_date_img, generate_datetime_img,
    generate_meteo_img,
    fetch_nba_results_img,
    fetch_library_info_img,
    assemble_img, publish_img,
    generate_stm_img
)
from edisplay.image_config import DATETIME_SIZE, METEO_PANEL_SIZE, STM_PANEL_SIZE


@scheduler.task(name='workflows.weekday_0600_0659_routine')
def weekday_0600_0659_routine():
    now = datetime.now()

    job = chain(
        group(
            generate_datetime_img.s(DATETIME_SIZE),
            generate_stm_img.s(['45N'], STM_PANEL_SIZE),
            generate_meteo_img.s(now, now, METEO_PANEL_SIZE),
            fetch_library_info_img.s()
        ),
        assemble_img.s(),
        publish_img.s()
    )
    return job.apply_async()


@scheduler.task(name='workflows.weekday_0700_0729_routine')
def weekday_0700_0729_routine():
    now = datetime.now()

    job = chain(
        group(
            generate_datetime_img.s(DATETIME_SIZE),
            generate_stm_img.s(['47E', '197E'], STM_PANEL_SIZE),
            generate_meteo_img.s(now, now, METEO_PANEL_SIZE),
            fetch_nba_results_img.s(now),
        ),
        assemble_img.s(),
        publish_img.s()
    )
    return job.apply_async()


@scheduler.task(name='workflows.weekday_0730_0829_routine')
def weekday_0730_0829_routine():
    now = datetime.now()

    job = chain(
        group(
            generate_datetime_img.s(DATETIME_SIZE),
            generate_meteo_img.s(now, now, METEO_PANEL_SIZE),
            fetch_nba_results_img.s(now),
        ),
        assemble_img.s(),
        publish_img.s()
    )
    return job.apply_async()


@scheduler.task(name='workflows.weekday_0830_2300_routine')
def weekday_0830_2300_routine():
    now = datetime.now()

    job = chain(
        group(
            generate_date_img.s(DATETIME_SIZE),
            generate_meteo_img.s(now, now, METEO_PANEL_SIZE),
            # biblio
            fetch_nba_results_img.s(now),
            # nba upcoming games
        ),
        assemble_img.s(),
        publish_img.s()
    )
    return job.apply_async()
