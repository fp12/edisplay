import os 

from PIL import Image, ImageOps, ImageText, ImageDraw
from celery import shared_task

from edisplay.image_config import WHITE, BLACK, IMG_MODE, STM_PANEL_SIZE
from edisplay.stm_info import STMRealtimeAPI
from edisplay.fonts import Audiowide, Fira


BUS_ICON = os.path.join('img', 'bus', 'bus-icon.jpg')
ARRIVALS_COUNT = 2
MAGIC_PADDING = -4  # don't ask


@shared_task
def generate_stm_img(stops):
    size = STM_PANEL_SIZE

    stops_info = []
    try:
        stm = STMRealtimeAPI()
        stops_info = stm.get_arrivals_display_multi(stops)
    except Exception as e:
        print(f'`generate_stm_img` raised an exception but it was handled: {e}')
        return {f'error-stm': e}

    with Image.open(BUS_ICON) as im:
        im = im.convert(IMG_MODE)
        ratio = im.width / im.height
        im = ImageOps.pad(im, size, color=WHITE, centering=(0.0, 0.5))
        d = ImageDraw.Draw(im, IMG_MODE)

        stops_count = len(stops_info)
        x = size[1] * ratio + 10
        for stop_index, stop_info in enumerate(stops_info):
            text = ImageText.Text(stop_info.stop_name, Audiowide.REGULAR.size(35))
            text_height = text.get_bbox()[3]
            total_height = text_height * stops_count
            y_padding = (size[1] - total_height) // (stops_count + 1)
            y = y_padding + (text_height + y_padding) * stop_index + MAGIC_PADDING
            d.text((x, y), text, BLACK)

            rect_coords = tuple([int(_x + __x) for _x, __x in zip(text.get_bbox(), (x - 1, y - 3, x + 2, y + 2))])
            d.rectangle(rect_coords, width=2)

            for arrival_index, arrival_info in enumerate(stop_info.arrivals[:ARRIVALS_COUNT]):
                time_text_content = f'{arrival_info.delta}+{arrival_info.delay}m' if arrival_info.delay != 0 else f'{arrival_info.delta}m'
                time_text = ImageText.Text(time_text_content, Fira.REGULAR.size(35))
                x_arr = 330 - time_text.get_bbox()[2] if arrival_index == 0 else 410 - time_text.get_bbox()[2]
                d.text((x_arr, y + 1), time_text, BLACK, align='right')

        return {'stm': im}
