import platform
import time
import gc
from functools import reduce

from PIL import Image, ImageShow
from celery import shared_task

from edisplay.image_config import WHITE, IMG_MODE, WIDTH, HEIGHT, SIZE, PADDING_DEFAULT


PADDING_BETWEEN = 40
MAX_PARTIAL_REFRESHES = 20
COUNT_PARTIAL_REFRESHES = MAX_PARTIAL_REFRESHES + 1 # start with a full refresh
EPD = None


def get_epd():
    global EPD
    if EPD is None:
        from edisplay.waveshare_epd import epd7in5_V2
        EPD = epd7in5_V2.EPD()
    return EPD


def reset_epd():
    global EPD
    EPD = None


@shared_task(queue='gpio')
def assemble_img(panels):
    im = Image.new(IMG_MODE, SIZE, WHITE)

    # merging the results (array of dict to single dict)
    images = reduce(lambda d1, d2: d1 | d2, panels)

    y = PADDING_DEFAULT

    def vertical_add_image(name):
        nonlocal y
        if im_new := images.get(name):
            x = int((WIDTH - im_new.width) // 2.0)
            im.paste(im_new, (x, y))
            y += im_new.height + PADDING_BETWEEN
            im_new.close()

    vertical_add_image('datetime')
    vertical_add_image('message')
    vertical_add_image('calendar')
    vertical_add_image('stm')
    vertical_add_image('meteo')
    vertical_add_image('library')
    vertical_add_image('nba')

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
        buffer = None
        try:
            epd = get_epd()
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

                epd.display_Partial(buffer, 0, 0, HEIGHT, WIDTH)
                display_time = time.time()

                COUNT_PARTIAL_REFRESHES += 1

            print(f'Image published successfully. {full_refresh_txt} Get[{init_start - start_time:.2f}s] Init[{init_time - init_start:.2f}s] Display[{display_time - init_time:.2f}s] Total[{display_time - start_time:.2f}s]')
        
        except Exception as e:
            print(f'Error publishing to display: {e}')
            reset_epd()
        
        finally:
            if buffer is not None:
                del buffer

            if im is not None:
                im.close()

            try:
                from edisplay.waveshare_epd import epdconfig
                epdconfig.module_exit()
            except Exception as e:
                print(f'Warning: module_exit failed: {e}')

            gc.collect()


@shared_task(queue='gpio')
def sleep_display():
    if platform.system() == 'Linux':
        buffer = None
        im = None
        try:
            epd = get_epd()
            epd.init()
            im = Image.new(IMG_MODE, SIZE, WHITE)
            buffer = epd.getbuffer(im)
            epd.display(buffer)
            epd.sleep()

            print(f'Getting to sleep.')

        except Exception as e:
            print(f'Error getting display to sleep: {e}')

        finally:
            if buffer is not None:
                del buffer
            
            if im is not None:
                im.close()

            reset_epd()

            gc.collect()
