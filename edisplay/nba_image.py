import json
import os

from PIL import Image, ImageOps, ImageShow, ImageText, ImageDraw

from edisplay.image_config import DEFAULT_COLOR, MODE_BW, INK_COLOR
from edisplay.fonts import Fira
from edisplay.nba_results import get_games


NBA_LOGO = os.path.join('img', 'nba', 'nba-logo-bw.jpg')
SAVED_GAMES = os.path.join('tmp', 'nba_results.json')

COLUMNS = 2
LINES = 4
MAX_GAMES = COLUMNS * LINES


def generate_image(date_from, date_to, size):
    with Image.open(NBA_LOGO) as im:
        im = im.convert(MODE_BW)
        ratio = im.width / im.height
        im = ImageOps.pad(im, size, color=DEFAULT_COLOR, centering=(0.0, 0.5))
        d = ImageDraw.Draw(im, MODE_BW)

        if not os.path.exists(SAVED_GAMES):
            with open(SAVED_GAMES, 'w') as f:
                json.dump({}, f)

        with open(SAVED_GAMES, mode='r+') as f:
            results = json.load(f)
            games = results.get(date_to, [])
            if not games:
                games = get_games(date_from, date_to)
                results[date_to] = games

                f.seek(0)
                f.truncate()
                json.dump(results, f)

            initial_x = size[1] * ratio
            for index, game in enumerate(games[:MAX_GAMES]):
                text = ImageText.Text(game, Fira.SEMIBOLD.size(18))
                text_width = text.get_bbox()[2]
                total_width = COLUMNS * text_width
                x_padding = (size[0] - total_width - initial_x) / (COLUMNS + 1)
                x = initial_x + x_padding
                if index > LINES - 1:
                    x += text_width + x_padding

                text_height = text.get_bbox()[3]
                total_height = text_height * LINES
                y_padding = (size[1] - total_height) / (LINES + 1)
                y = y_padding + (index % LINES) * (text_height + y_padding)
                d.text((x, y), text, INK_COLOR)

        return im


def generate_nba_image(games, size):
    with Image.open(NBA_LOGO) as im:
        im = im.convert(MODE_BW)
        ratio = im.width / im.height
        im = ImageOps.pad(im, size, color=DEFAULT_COLOR, centering=(0.0, 0.5))
        d = ImageDraw.Draw(im, MODE_BW)

        initial_x = size[1] * ratio
        for index, game in enumerate(games[:MAX_GAMES]):
            text = ImageText.Text(game, Fira.SEMIBOLD.size(18))
            text_width = text.get_bbox()[2]
            total_width = COLUMNS * text_width
            x_padding = (size[0] - total_width - initial_x) / (COLUMNS + 1)
            x = initial_x + x_padding
            if index > LINES - 1:
                x += text_width + x_padding

            text_height = text.get_bbox()[3]
            total_height = text_height * LINES
            y_padding = (size[1] - total_height) / (LINES + 1)
            y = y_padding + (index % LINES) * (text_height + y_padding)
            d.text((x, y), text, INK_COLOR)
        
        return im


if __name__ == '__main__':
    im = generate_image('2025-12-12', '2025-12-17', (460, 100))
    ImageShow.show(im)
