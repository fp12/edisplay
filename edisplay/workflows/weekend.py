from datetime import datetime

from celery import chain, group, shared_task

from edisplay.tasks.time import generate_date_img
from edisplay.tasks.nba import fetch_nba_results_img
from edisplay.tasks.image import assemble_img, publish_img


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
