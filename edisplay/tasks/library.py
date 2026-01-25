from datetime import datetime
from pathlib import Path

from babel.dates import format_date
from PIL import Image, ImageOps, ImageShow, ImageText, ImageDraw
from celery import shared_task

from edisplay.image_config import WHITE, BLACK, IMG_MODE, WIDTH, PADDING_DEFAULT, LIBRARY_PANEL_SIZE
from edisplay.fonts import Fira
from edisplay.spreadsheet import get_table_content
from edisplay.secrets import get_secret
from edisplay.tasks.utils import clear_cached_images


LIBRARY_LOGO = Path('img') / 'library' / 'book-cover_BW.jpg'
BASE_COORDS = (0, 2, 270, 24)


def generate_library_info_image(info):
    with Image.open(LIBRARY_LOGO) as im:
        im = im.convert(IMG_MODE)
        ratio = im.width / im.height
        im = ImageOps.pad(im, LIBRARY_PANEL_SIZE, color=WHITE, centering=(0.0, 0.5))
        d = ImageDraw.Draw(im, IMG_MODE)

        initial_x = LIBRARY_PANEL_SIZE[1] * ratio

        x = initial_x + PADDING_DEFAULT
        y = 1

        order = get_secret('Library', 'Order')
        info_dict = dict(info)
        for key in order:
            value = info_dict[key]
            date = datetime.fromisoformat(value)
            date_formatted = format_date(date, format="d MMMM", locale='fr_FR')
            text = ImageText.Text(f'{key} -> {date_formatted}', Fira.LIGHT.size(20))
            rect_coords = tuple([int(_x + __x) for _x, __x in zip(BASE_COORDS, (x - 6, y - 2, x + 6, y + 2))])
            d.rounded_rectangle(rect_coords, radius=30, outline=BLACK, width=2)
            d.text((x, y), text, BLACK, features=['+liga'])
            y = rect_coords[3] - 1

    return im


@shared_task
def cache_library_info():
    spreadsheet_id = get_secret('Google', 'SpreadsheetId')
    table_id = get_secret('Google', 'TableId')
    sheet_info = get_table_content(spreadsheet_id, table_id)
    
    last_modified = sheet_info['last_modified']
    last_modified = format_date(last_modified, format='yyyy-MM-dd') if isinstance(last_modified, datetime) else last_modified

    im_path = Path('tmp') / f'library_info_{last_modified}.png'
    if not im_path.exists():
        def date_to_iso(date):
            return format_date(datetime.strptime(date, '%d/%m/%Y'), format='yyyy-MM-dd')

        im_info = [(name, date_to_iso(date)) for name, _, date in sheet_info['rows'][1:]]
        
        if im := generate_library_info_image(im_info):
            im.save(im_file_path)
        else:
            print('Something went wrong during the library image generation')


@shared_task
def clear_cached_library_info():
    clear_cached_images('library_info_*.png')


@shared_task
def fetch_library_info_img():
    files = list(Path('tmp').glob('library_info_*.png'))
    if not files:
        return None

    latest = max(files, key=lambda f: f.stem.split('library_info_')[1])
    if Path(latest).exists():
        print(f'Loading cached library image from {latest}')
        with Image.open(latest) as im:
            # Create a copy so we can close the file safely
            return {'library': im.copy()}


if __name__ == '__main__':
    info = [
        ('AAAAA', '2026-02-02'),
        ('BBBBBBB', '2026-04-12'),
        ('CCCCCCCC', '2026-01-16'),
        ('DDD', '2026-02-27')
    ]
    im = generate_library_info_image(info)
    ImageShow.show(im)
