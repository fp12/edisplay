import platform
import time
from functools import reduce

from PIL import Image, ImageShow
from celery import shared_task

from edisplay.image_config import WHITE, IMG_MODE, WIDTH, HEIGHT, SIZE, PADDING_DEFAULT


PADDING_BETWEEN = 50
MAX_PARTIAL_REFRESHES = 20
COUNT_PARTIAL_REFRESHES = MAX_PARTIAL_REFRESHES + 1 # start with a full refresh


@shared_task(queue='gpio')
def assemble_img(panels):
    im = Image.new(IMG_MODE, SIZE, WHITE)

    # merging the results (array of dict to single dict)
    images = reduce(lambda d1, d2: d1 | d2, panels)

    y = PADDING_DEFAULT

    if im_datetime := images.get('datetime'):
        x = int((WIDTH - im_datetime.width) // 2.0)
        im.paste(im_datetime, (x, y))
        y += im_datetime.height + PADDING_BETWEEN

    if im_message := images.get('message'):
        x = int((WIDTH - im_message.width) / 2.0)
        im.paste(im_message, (x, y))
        y += im_message.height + PADDING_BETWEEN

    if im_calendar := images.get('calendar'):
        x = int((WIDTH - im_calendar.width) / 2.0)
        im.paste(im_calendar, (x, y))
        y += im_calendar.height + PADDING_BETWEEN

    if im_stm := images.get('stm'):
        x = int((WIDTH - im_stm.width) / 2.0)
        im.paste(im_stm, (x, y))
        y += im_stm.height + PADDING_BETWEEN

    if im_meteo := images.get('meteo'):
        x = int((WIDTH - im_meteo.width) / 2.0)
        im.paste(im_meteo, (x, y))
        y += im_meteo.height + PADDING_BETWEEN

    if im_library := images.get('library'):
        x = int((WIDTH - im_library.width) / 2.0)
        im.paste(im_library, (x, y))
        y += im_library.height + PADDING_BETWEEN

    if im_nba := images.get('nba'):
        x = int((WIDTH - im_nba.width) / 2.0)
        y = HEIGHT - im_nba.height - PADDING_DEFAULT
        im.paste(im_nba, (x, y))

    return im


@shared_task(queue='gpio')
def publish_img(im, full_refresh=False):
    global COUNT_PARTIAL_REFRESHES

    if full_refresh:
        COUNT_PARTIAL_REFRESHES = MAX_PARTIAL_REFRESHES + 1
    
    start_time = time.time()
    os_name = platform.system()
    if os_name == 'Windows':
        ImageShow.show(im)
    elif os_name == 'Linux':
        try:
            from edisplay.waveshare_epd import epd7in5_V2
            import_time = time.time()

            epd = epd7in5_V2.EPD()
            init_start = time.time()
            init_time = 0
            display_time = 0

            full_refresh_txt = 'FullRefresh' if COUNT_PARTIAL_REFRESHES >= MAX_PARTIAL_REFRESHES else 'PartialRefresh'

            buffer = epd.getbuffer(im)

            if COUNT_PARTIAL_REFRESHES >= MAX_PARTIAL_REFRESHES:
                epd.init()
                init_time = time.time()

                epd.display(buffer)
                display_time = time.time()
                
                COUNT_PARTIAL_REFRESHES = 0
            else:
                epd.init_part()
                init_time = time.time()

                epd.display_Partial(buffer, 0, 0, 800, 480)
                display_time = time.time()

                COUNT_PARTIAL_REFRESHES += 1

            print(f'Image published successfully. {full_refresh_txt} Im[{import_time - start_time:.2f}s] Ob[{init_start - import_time:.2f}s] In[{init_time - init_start:.2f}s] Di[{display_time - init_time:.2f}s] To[{display_time - start_time:.2f}s]')
        
        except Exception as e:
            print(f'Error publishing to display: {e}')
        
        finally:
            if buffer is not None:
                del buffer

            import gc
            gc.collect()


@shared_task(queue='gpio')
def sleep_display():
    os_name = platform.system()
    if os_name == 'Linux':
        from edisplay.waveshare_epd import epd7in5_V2

        epd = None
        try:
            epd = epd7in5_V2.EPD()
            epd.init()
            im = Image.new(IMG_MODE, SIZE, WHITE)
            epd.display(epd.getbuffer(im))
            epd.sleep()
        except Exception as e:
            print(f'Error getting display to sleep: {e}')
