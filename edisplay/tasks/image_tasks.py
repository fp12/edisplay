import platform
import time
from functools import reduce

from edisplay.scheduler import scheduler

from PIL import Image, ImageShow

from edisplay.image_config import WHITE, IMG_MODE, WIDTH, HEIGHT, SIZE, PADDING_DEFAULT


PADDING_BETWEEN = 50


@scheduler.task(name='tasks.assemble_img')
def assemble_img(panels):
    im = Image.new(IMG_MODE, SIZE, WHITE)

    # merging the results (array of dict to single dict)
    images = reduce(lambda d1, d2: d1 | d2, panels)

    y = PADDING_DEFAULT

    if im_datetime := images.get('datetime'):
        x = int((WIDTH - im_datetime.width) // 2.0)
        im.paste(im_datetime, (x, y))
        y += im_datetime.height + PADDING_BETWEEN

    if im_stm := images.get('stm'):
        x = int((WIDTH - im_stm.width) / 2.0)
        im.paste(im_stm, (x, y))
        y += im_stm.height + PADDING_BETWEEN

    if im_meteo := images.get('meteo'):
        x = int((WIDTH - im_meteo.width) / 2.0)
        im.paste(im_meteo, (x, y))
        y += im_meteo.height + PADDING_BETWEEN

    if im_nba := images.get('nba'):
        x = int((WIDTH - im_nba.width) / 2.0)
        y = HEIGHT - im_nba.height - PADDING_DEFAULT
        im.paste(im_nba, (x, y))

    return im


@scheduler.task(name='tasks.publish_img', queue='gpio')
def publish_img(im):
    start_time = time.time()
    os_name = platform.system()
    if os_name == 'Windows':
        ImageShow.show(im)
    elif os_name == 'Linux':
        from edisplay.waveshare_epd import epd7in5_V2
        import_time = time.time()
        print(f"Import time: {import_time - start_time:.2f}s")

        epd = None
        try:
            epd = epd7in5_V2.EPD()
            init_start = time.time()
            print(f"EPD object creation: {init_start - import_time:.2f}s")
            
            epd.init_4Gray()
            init_time = time.time()
            print(f"EPD init: {init_time - init_start:.2f}s")

            epd.display_4Gray(epd.getbuffer_4Gray(im))
            display_time = time.time()
            print(f"Display: {display_time - init_time:.2f}s")

            print(f"Total time: {display_time - start_time:.2f}s")

            print('Image published successfully')
        except Exception as e:
            print(f'Error publishing to display: {e}')


@scheduler.task
def sleep_display():
    start_time = time.time()
    os_name = platform.system()
    if os_name == 'Linux':
        from edisplay.waveshare_epd import epd7in5_V2
        import_time = time.time()
        print(f"Import time: {import_time - start_time:.2f}s")

        epd = None
        try:
            epd = epd7in5_V2.EPD()
            init_start = time.time()
            print(f"EPD object creation: {init_start - import_time:.2f}s")

            epd.sleep()
            sleep_time = time.time()
            print(f"Sleep: {sleep_time - init_start:.2f}s")
        except Exception as e:
            print(f'Error getting display to sleep: {e}')
