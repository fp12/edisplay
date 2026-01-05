from datetime import datetime

from celery import chain, group

from edisplay.scheduler import scheduler
from edisplay.tasks import (
    generate_date_img, generate_datetime_img,
    generate_meteo_img,
    generate_nba_results_img,
    assemble_img, display_img,
    generate_stm_img
)
from edisplay.image_config import DATETIME_SIZE, METEO_PANEL_SIZE, STM_PANEL_SIZE, NBA_PANEL_SIZE


@scheduler.task(name='workflows.weekday_6_730_routine')
def weekday_6_730_routine():
    now = datetime.now()

    job = chain(
        group(
            generate_datetime_img.s(DATETIME_SIZE),
            generate_stm_img.s(['45N', '47E', '197E'], STM_PANEL_SIZE),
            generate_meteo_img.s(now, now, METEO_PANEL_SIZE),
            generate_nba_results_img.s(now, NBA_PANEL_SIZE),
        ),
        assemble_img.s(),
        display_img.s()
    )
    return job.apply_async()


@scheduler.task(name='workflows.weekday_6_8_routine')
def weekday_730_830_routine():
    now = datetime.now()

    job = chain(
        group(
            generate_datetime_img.s(DATETIME_SIZE),
            generate_meteo_img.s(now, now, METEO_PANEL_SIZE),
            generate_nba_results_img.s(now, NBA_PANEL_SIZE),
        ),
        assemble_img.s(),
        display_img.s()
    )
    return job.apply_async()


@scheduler.task(name='workflows.weekday_6_8_routine')
def weekday_830_23_routine():
    now = datetime.now()

    job = chain(
        group(
            generate_date_img.s(DATETIME_SIZE),
            # meteo trends
            # biblio
            # nba results + upcoming games
        ),
        assemble_img.s(),
        display_img.s()
    )
    return job.apply_async()
