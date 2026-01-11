import json
from datetime import datetime
from pathlib import Path

from babel.dates import format_date
from PIL import Image, ImageOps, ImageShow, ImageText, ImageDraw

from edisplay.image_config import WHITE, GRAY2, BLACK, IMG_MODE, WIDTH, PADDING_DEFAULT, LIBRARY_PANEL_SIZE
from edisplay.fonts import Fira
from edisplay.scheduler import scheduler
from edisplay.spreadsheet import get_table_content
from edisplay.secrets import get_config


CACHED_LIBRARY_INFO = Path('tmp') / 'library_info.json'
LIBRARY_LOGO = Path('img') / 'library' / 'book-cover_L.jpg'
BASE_COORDS = (0, 2, 264, 24)


def generate_library_info_image(info):
    with Image.open(LIBRARY_LOGO) as im:
        ratio = im.width / im.height
        im = ImageOps.pad(im, LIBRARY_PANEL_SIZE, color=WHITE, centering=(0.0, 0.5))
        d = ImageDraw.Draw(im, IMG_MODE)

        initial_x = LIBRARY_PANEL_SIZE[1] * ratio

        x = initial_x + PADDING_DEFAULT
        y = 1

        for entry in info:
            date = datetime.fromisoformat(entry[1])
            date_formatted = format_date(date, format="d MMMM", locale='fr_FR')
            text = ImageText.Text(f'{entry[0]} -> {date_formatted}', Fira.LIGHT.size(20))
            rect_coords = tuple([int(_x + __x) for _x, __x in zip(BASE_COORDS, (x - 6, y - 2, x + 6, y + 2))])
            print(text.get_bbox())
            print(rect_coords, rect_coords[3] - rect_coords[1])
            d.rounded_rectangle(rect_coords, radius=30, outline=GRAY2, width=2)
            d.text((x, y), text, BLACK)
            y = rect_coords[3] - 1

    return im


@scheduler.task
def cache_library_info():
    spreadsheet_id = get_config('Google', 'SpreadsheetId')
    table_id = get_config('Google', 'TableId')
    info = get_table_content(spreadsheet_id, table_id)
    
    last_modified = info['last_modified']
    last_modified = format_date(last_modified, format='yyyy-MM-dd') if isinstance(last_modified, datetime) else last_modified

    def date_to_iso(date):
        print(date)
        print(datetime.strptime(date, '%d/%m/%Y'))
        return format_date(datetime.strptime(date, '%d/%m/%Y'), format='yyyy-MM-dd')

    with open(CACHED_LIBRARY_INFO, mode='r+') as f:
        library_info = json.load(f)
        if library_info.get(last_modified) is None:
            library_info[last_modified] = [(name, date_to_iso(date)) for name, _, date in info['rows'][1:]]

            f.seek(0)
            f.truncate()
            json.dump(library_info, f)

            im_file_path = Path('tmp') / f'library_info_{last_modified}.png'
            im = generate_library_info_image(library_info[last_modified])
            im.save(im_file_path)


@scheduler.task
def clear_cached_library_info():
    with open(CACHED_LIBRARY_INFO, 'w') as f:
        json.dump({}, f)

    directory_path = Path('tmp')
    pattern = 'library_info_*.png'
    for file_path in directory_path.glob(pattern):
        try:
            if file_path.is_file():
                file_path.unlink()
                print(f'Deleted: {file_path}')
        except OSError as e:
            print(f'Error deleting {file_path}: {e}')


if __name__ == '__main__':
    info = [
        ('AAAAA', '2026-02-02'),
        ('BBBBBBB', '2026-04-12'),
        ('CCCCCCCC', '2026-01-16'),
        ('DDD', '2026-02-27')
    ]
    im = generate_library_info_image(info)
    ImageShow.show(im)
