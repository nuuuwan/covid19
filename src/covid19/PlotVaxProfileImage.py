from PIL import Image, ImageDraw, ImageFont
from utils import timex

from covid19 import epid

BASE_IMAGE_FILE = 'src/covid19/assets/lk_map.png'
FONT_FILE = 'src/covid19/assets/Arial.ttf'

POPULATION = 21_800_000
PADDING = 0.12
WINDOW_DAYS_AND_COLOR = [(7, 'green'), (28, 'orange'), (112, 'red')]


def _draw():
    timeseries = epid.load_timeseries()
    latest_item = timeseries[-1]
    y = list(
        map(
            lambda d: d['cum_total'],
            timeseries,
        )
    )
    date_id = timex.format_time(latest_item['ut'], '%Y%m%d')
    timex.SECONDS_IN.DAY
    cum_total = y[-1]
    goal = POPULATION * 4 / 3
    p_goal = cum_total / goal

    stat_text = '{:.1%}'.format(p_goal)
    color = 'green'
    subtitle = 'of Goal'

    im = Image.open(BASE_IMAGE_FILE)
    im_color = Image.new("RGB", im.size, (255, 255, 255))
    im_color.paste(im)

    width, height = im_color.size
    dim = min(width, height)
    im_cropped = im_color.crop((0, 0, dim, dim))

    dim_mid = (int)(dim * 0.5)
    draw = ImageDraw.Draw(im_cropped)
    font_size = (int)(1.2 * dim / len(stat_text))
    font = ImageFont.truetype(FONT_FILE, font_size)
    draw.text(
        (dim_mid, dim_mid),
        stat_text,
        fill=color,
        font=font,
        anchor='mm',
    )

    font_smaller = ImageFont.truetype(FONT_FILE, (int)(font_size / 3))
    draw.text(
        (dim_mid, dim_mid + 2 * font_size / 3),
        subtitle,
        fill=color,
        font=font_smaller,
        anchor='mm',
    )
    profile_image_file = '/tmp/covid19.vax.profile.%s.png' % (date_id)
    im_cropped.save(profile_image_file)
    return profile_image_file
