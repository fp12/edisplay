from typing import List

from PIL import Image, ImageOps, ImageShow, ImageText, ImageDraw

from edisplay.image_config import DEFAULT_COLOR, MODE_BW, INK_COLOR
from edisplay.fonts import Audiowide, Fira
from edisplay.stm_info import STMRealtimeAPI


BUS_ICON = 'img/bus/bus-icon.jpg'
ARRIVALS_COUNT = 2
MAGIC_PADDING = -4  # don't ask


def generate_image(stops : List[str], size):
    stm = STMRealtimeAPI()

    with Image.open(BUS_ICON) as im:
        im = im.convert(MODE_BW)
        ratio = im.width / im.height
        im = ImageOps.pad(im, size, color=DEFAULT_COLOR, centering=(0.0, 0.5))
        d = ImageDraw.Draw(im, MODE_BW)

        stops_count = len(stops)
        x = size[1] * ratio + 10
        stops_info = stm.get_arrivals_display_multi(stops)
        for stop_index, stop_info in enumerate(stops_info):
            text = ImageText.Text(stop_info.stop_name, Audiowide.REGULAR.size(35))
            text_height = text.get_bbox()[3]
            total_height = text_height * stops_count
            y_padding = (size[1] - total_height) // (stops_count + 1)
            y = y_padding + (text_height + y_padding) * stop_index + MAGIC_PADDING
            d.text((x, y), text, INK_COLOR)

            rect_coords = tuple([int(_x + __x) for _x, __x in zip(text.get_bbox(), (x - 1, y - 3, x + 2, y + 2))])
            d.rectangle(rect_coords, width=2)

            for arrival_index, arrival_info in enumerate(stop_info.arrivals[:ARRIVALS_COUNT]):
                time_text_content = f'{arrival_info.delta}+{arrival_info.delay}m' if arrival_info.delay != 0 else f'{arrival_info.delta}m'
                time_text = ImageText.Text(time_text_content, Fira.REGULAR.size(35))
                x_arr = 330 - time_text.get_bbox()[2] if arrival_index == 0 else 410 - time_text.get_bbox()[2]
                d.text((x_arr, y + 1), time_text, INK_COLOR, align='right')

        return im


if __name__ == '__main__':
    im = generate_image(['47E', '197E', '45N'], (460, 150))
    ImageShow.show(im)
