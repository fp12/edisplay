from functools import reduce

from edisplay.scheduler import scheduler

from PIL import Image, ImageShow

from edisplay.image_config import DEFAULT_COLOR, MODE_BW, WIDTH, HEIGHT, SIZE, PADDING_DEFAULT


@scheduler.task(name='tasks.assemble_img')
def assemble_img(panels):
    im = Image.new(MODE_BW, SIZE, DEFAULT_COLOR)

    # merging the results (array of dict to single dict)
    images = reduce(lambda d1, d2: d1 | d2, panels)

    y = PADDING_DEFAULT

    if im_datetime := images.get('datetime'):
        x = int((WIDTH - im_datetime.width) // 2.0)        
        im.paste(im_datetime, (x, y))
        y += im_datetime.height + PADDING_DEFAULT

    if im_stm := images.get('stm'):
        x = int((WIDTH - im_stm.width) / 2.0)
        im.paste(im_stm, (x, y))
        y += im_stm.height + PADDING_DEFAULT

    if im_meteo := images.get('meteo'):
        x = int((WIDTH - im_meteo.width) / 2.0)
        im.paste(im_meteo, (x, y))
        y += im_meteo.height + PADDING_DEFAULT

    if im_nba := images.get('nba'):
        x = int((WIDTH - im_nba.width) / 2.0)
        y = HEIGHT - im_nba.height - PADDING_DEFAULT
        im.paste(im_nba, (x, y))
        y += im_nba.height + PADDING_DEFAULT

    return im


@scheduler.task(name='tasks.display_img')
def display_img(img):
    ImageShow.show(img)
