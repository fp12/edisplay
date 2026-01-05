import os

from PIL import Image, ImageShow, ImageText, ImageDraw

from edisplay.image_config import DEFAULT_COLOR, MODE_BW, INK_COLOR
from edisplay.fonts import Quicksand, Fira
from edisplay.meteo_info import get_info


def get_icon_path(file_name):
    return os.path.join('img', 'meteo', file_name)


def get_weather_icon(weather_code):
    """
    Code	Description
    0	Clear sky
    1, 2, 3	Mainly clear, partly cloudy, and overcast
    45, 48	Fog and depositing rime fog
    51, 53, 55	Drizzle: Light, moderate, and dense intensity
    56, 57	Freezing Drizzle: Light and dense intensity
    61, 63, 65	Rain: Slight, moderate and heavy intensity
    66, 67	Freezing Rain: Light and heavy intensity
    71, 73, 75	Snow fall: Slight, moderate, and heavy intensity
    77	Snow grains
    80, 81, 82	Rain showers: Slight, moderate, and violent
    85, 86	Snow showers slight and heavy
    95 *	Thunderstorm: Slight or moderate
    96, 99 *	Thunderstorm with slight and heavy hail
    """
    path = ''
    match weather_code:
        case 0.0:
            path = 'wi-day-sunny.png'
        case 1.0 | 2.0:
            path = 'wi-day-sunny-overcast.png'
        case 3.0:
            path = 'wi-cloud.png'
        case 45.0 | 48.0:
            path = 'wi-day-fog.png'
        # case 51.0 | 53.0 | 55.0:
        # case 56.0 | 57.0:
        case 61.0 | 63.0 | 65.0:
            path = 'wi-day-rain.png'
        # case 66.0 | 67.0:
        case 71.0 | 73.0 | 75.0:
            path = 'wi-day-snow.png'
        # case 77.0:
        case 80.0 | 81.0 | 82.0:
            path = 'wi-day-showers.png'
        case 85.0 | 86.0:
            path = 'wi-day-snow.png'
        case 95.0:
            path = 'wi-thunderstorm.png'
        case 96.0 | 99.0:
            path = 'wi-thunderstorm.png'

    if path:
        path = get_icon_path(path)
        with Image.open(path) as im:
            im.load()
            return im
    else:
        im = Image.new(MODE_BW, (32, 32), DEFAULT_COLOR)
        d = ImageDraw.Draw(im, MODE_BW)
        text = ImageText.Text(f'{weather_code}', Fira.RETINA.size(28))
        d.text((0, 0), text, INK_COLOR)
        return im


def generate_image(date_from, date_to, size):
    meteo_current, meteo_daily = get_info(date_from, date_to)
    icon = get_weather_icon(meteo_current.weather_code)

    im = Image.new(MODE_BW, size, DEFAULT_COLOR)
    im.paste(icon, (0, 10))
    d = ImageDraw.Draw(im)
    text = ImageText.Text(f'{meteo_current.temperature_2m:.0f}°|{meteo_current.apparent_temperature:.0f}°', Quicksand.BOLD.size(50))
    x = icon.getbbox()[2] + 5
    y = 20
    d.text((x, y), text, INK_COLOR)

    has_rain = meteo_current.rain > 0.0
    has_snow = meteo_current.snowfall > 0.0

    if has_rain:
        with Image.open(get_icon_path('wi-raindrop.png')) as im_rain:
            x_rain = x + text.get_bbox()[2]
            y_rain = y + 10 if not has_snow else y - 10
            im_rain = im_rain.convert('RGB').resize((48, 48), Image.Resampling.LANCZOS)
            im.paste(im_rain, (x_rain, y_rain))
            text_rain = ImageText.Text(f'{meteo_current.rain:.0f}mm', Quicksand.REGULAR.size(32))
            x_rain += im_rain.getbbox()[2] - 10
            d.text((x_rain, y_rain), text_rain)

    if has_snow:
        with Image.open(get_icon_path('wi-snowflake-cold.png')) as im_snow:
            x_snow = x + text.get_bbox()[2]
            y_snow = y + 25 if has_rain else y + 10
            im_snow = im_snow.convert('RGB').resize((48, 48), Image.Resampling.LANCZOS)
            im.paste(im_snow, (x_snow, y_snow))
            text_snow = ImageText.Text(f'{meteo_current.snowfall:.0f}cm', Quicksand.REGULAR.size(32))
            x_snow += im_snow.getbbox()[2] - 10
            d.text((x_snow, y_snow + 3), text_snow)

    with Image.open(get_icon_path('wi-time-8.png')) as im_time:
        x_time = 10
        y_time = y + text.get_bbox()[3] + 18
        im_time = im_time.convert('RGB').resize((48, 48), Image.Resampling.BILINEAR)
        im.paste(im_time, (x_time, y_time))

    with Image.open(get_icon_path('wi-raindrop.png')) as im_rain:
        x_rain = 60
        y_rain = y + text.get_bbox()[3] + 20
        im_rain = im_rain.convert('RGB').resize((48, 48), Image.Resampling.LANCZOS)
        im.paste(im_rain, (x_rain, y_rain))
        text_rain = ImageText.Text(f'{meteo_daily.rain_sum:.0f}mm', Quicksand.REGULAR.size(32))
        x_rain += im_rain.getbbox()[2] - 10
        d.text((x_rain, y_rain), text_rain)

    with Image.open(get_icon_path('wi-snowflake-cold.png')) as im_snow:
        x_snow = 180
        y_snow = y + text.get_bbox()[3] + 17
        im_snow = im_snow.convert('RGB').resize((48, 48), Image.Resampling.LANCZOS)
        im.paste(im_snow, (x_snow, y_snow))
        text_snow = ImageText.Text(f'{meteo_daily.snowfall_sum:.0f}cm', Quicksand.REGULAR.size(32))
        x_snow += im_snow.getbbox()[2] - 10
        d.text((x_snow, y_snow + 3), text_snow)

    return im


if __name__ == '__main__':
    im = generate_image('2025-12-22', '2025-12-22', (460, 150))
    ImageShow.show(im)
