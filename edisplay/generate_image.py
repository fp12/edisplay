from io import BytesIO
from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageShow, ImageText
from babel.dates import format_date, format_time

from edisplay.image_config import DEFAULT_COLOR, MODE_BW, WIDTH, HEIGHT, SIZE, INK_COLOR
from edisplay.fonts import Fira, Quicksand
from edisplay.stm_image import generate_image as stm_image
from edisplay.nba_image import generate_image as nba_image
from edisplay.meteo_image import generate_image as meteo_image

STM_PANEL_SIZE = (WIDTH - 20, 150)
METEO_PANEL_SIZE = (WIDTH - 20, 150)
NBA_PANEL_SIZE = (WIDTH - 20, 100)
PADDING_DEFAULT = 10


def generate_binary(debug=False):
    im = Image.new(MODE_BW, SIZE, DEFAULT_COLOR)
    d = ImageDraw.Draw(im, MODE_BW)

    ### DATE / TIME
    now = datetime.now()
    formatted_date = format_date(now, format="EEEE d MMMM", locale='fr_FR')
    formatted_time = format_time(now, format="H:mm", locale='fr_FR')

    text = ImageText.Text(formatted_date, Quicksand.LIGHT.size(25))
    x = (WIDTH - text.get_length()) / 2.0
    y = PADDING_DEFAULT
    d.text((x, y), text, INK_COLOR)

    y += text.get_bbox()[3] + PADDING_DEFAULT
    text = ImageText.Text(formatted_time, Fira.RETINA.size(100))
    x = (WIDTH - text.get_length()) / 2.0
    d.text((x, y), text, INK_COLOR)
    y += text.get_bbox()[3] + 50
    ### DATE / TIME

    ### STM
    if im_stm := stm_image(['45N', '47E', '197E'], STM_PANEL_SIZE):
        x = int((WIDTH - im_stm.width) / 2.0)
        im.paste(im_stm, (x, y))
        y += im_stm.height + 50
    ### STM

    ### METEO
    now_formatted = format_date(now, format='yyyy-MM-dd')
    if im_meteo := meteo_image(now_formatted, now_formatted, METEO_PANEL_SIZE):
        x = int((WIDTH - im_meteo.width) / 2.0)
        im.paste(im_meteo, (x, y))
    ### METEO

    ### NBA Results
    nba_date_from = now
    nba_date_to = now - timedelta(days=1)  # yesterday
    if now.weekday == 0: # Monday
        nba_date_from -= timedelta(days=3)
    else:
        nba_date_from = nba_date_to
    
    if im_nba := nba_image(format_date(nba_date_from, format='yyyy-MM-dd'), format_date(nba_date_to, format='yyyy-MM-dd'), NBA_PANEL_SIZE):
        x = int((WIDTH - im_nba.width) / 2.0)
        y = HEIGHT - im_nba.height - PADDING_DEFAULT
        im.paste(im_nba, (x, y))
    ### NBA Results

    if debug:
        ImageShow.show(im)
        return None

    img_io = BytesIO()
    im.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io.getvalue()


if __name__ == '__main__':
    generate_binary(debug=True)
