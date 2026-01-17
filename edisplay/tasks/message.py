from datetime import datetime, time

from celery import shared_task
from PIL import Image, ImageDraw, ImageText

from edisplay.secrets import get_secret
from edisplay.image_config import IMG_MODE, WHITE, BLACK, MESSAGE_SIZE, PADDING_DEFAULT, WIDTH
from edisplay.fonts import Quicksand


def get_content_for_time(category, now_time):
    messages = get_secret('Messages', category)
    if messages is None:
        print(f'Unknown message category: {category}')
        return None

    selected_content = None

    for message in messages:
        hours, minutes = message['time'].split(':')
        msg_time = time(hour=int(hours), minute=int(minutes))
        if msg_time < now_time:
            selected_content = message['content']

    if selected_content is None:
        print(f'No content for time {now_time} in category: {category}')

    return selected_content


@shared_task
def generate_message_img(category):
    now_time = datetime.now().time()
    if content := get_content_for_time(category, now_time):
        im = Image.new(IMG_MODE, MESSAGE_SIZE, WHITE)
        d = ImageDraw.Draw(im, IMG_MODE)

        text = ImageText.Text(content, Quicksand.SEMIBOLD.size(35))

        x = (WIDTH - text.get_length()) / 2.0
        y = 0
        d.text((x, y), text, BLACK)

        return {'message': im}

    return {}


if __name__ == '__main__':
    now_time = time(hour=9, minute=45)
    result = generate_message_img('weekday_morning')
    print(result)
    result['message'].save('message.png')
