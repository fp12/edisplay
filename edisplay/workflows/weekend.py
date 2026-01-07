from datetime import datetime

from celery import chain, group

from edisplay.scheduler import scheduler
from edisplay.tasks import (
    generate_date_img,
    generate_nba_results_img,
    assemble_img, publish_img,
)

from edisplay.image_config import DATETIME_SIZE, METEO_PANEL_SIZE, STM_PANEL_SIZE, NBA_PANEL_SIZE


@scheduler.task(name='workflows.weekend_6_23_routine')
def weekend_6_23_routine():
    now = datetime.now()
    
    job = chain(
        group(
            generate_date_img.s(DATETIME_SIZE),
            # generate_meteo_img.s(now, now, METEO_PANEL_SIZE),
            generate_nba_results_img.s(now, NBA_PANEL_SIZE),
        ),
        assemble_img.s(),
        publish_img.s()
    )
    return job.apply_async()
