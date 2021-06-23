"""Example 10."""

import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from utils import timex

from covid19 import lk_data, covid_data

BASE_IMAGE_FILE = 'src/covid19/assets/lk_map.png'
FONT_FILE = 'src/covid19/assets/Arial.ttf'

DAYS_TO_PLOT = 90
MOVING_AVG_WINDOW = 14
POPULATION = 21_800_000


def _plot_with_time_window(
    field_key,
    main_color,
    sub_color,
    label,
    is_background_image=False,
):
    timeseries = lk_data.get_timeseries()
    date_id = timex.format_time(timeseries[-1]['unixtime'], '%Y%m%d')
    date = timex.format_time(timeseries[-1]['unixtime'], '%Y-%m-%d')
    x = list(map(
        lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
        timeseries[-DAYS_TO_PLOT:],
    ))
    y = list(map(
        lambda d: d[field_key],
        timeseries[-DAYS_TO_PLOT:],
    ))
    plt.bar(x, y, color=sub_color)

    x2 = list(map(
        lambda d: datetime.datetime.fromtimestamp(d['unixtime'] \
            + MOVING_AVG_WINDOW * 86400),
        timeseries[(-DAYS_TO_PLOT - MOVING_AVG_WINDOW):],
    ))
    y2 = list(map(
        lambda d: d[field_key],
        timeseries[(-DAYS_TO_PLOT - MOVING_AVG_WINDOW):],
    ))
    y2 = np.convolve(y2, np.ones(MOVING_AVG_WINDOW) / MOVING_AVG_WINDOW, 'valid')

    plt.plot(x2[:-(MOVING_AVG_WINDOW - 1)], y2, color=main_color)
    plt.title(
        '%s with a %d-day moving average (as of %s)' % (
            label,
            MOVING_AVG_WINDOW,
            date,
        ),
    )
    plt.suptitle(
        'Data: https://github.com/CSSEGISandData/COVID-19; '
        + 'https://www.hpb.health.gov.lk/api/get-current-statistical; '
        + 'https://github.com/owid/covid-19-data',
        fontsize=8,
    )

    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(
        tkr.FuncFormatter(lambda x, p: format(int(x), ','))
    )

    fig = plt.gcf()
    fig.autofmt_xdate()
    fig_width = 12
    aspect_ratio = 3 if is_background_image else 16/9
    fig_height = round(fig_width / aspect_ratio, 1)
    fig.set_size_inches(fig_width, fig_height)

    background_label = 'background' if is_background_image else 'feed'
    image_file = '/tmp/covid19.plot.%s.%s.%s.window.png' % (
        date_id,
        field_key,
        background_label,
    )
    fig.savefig(image_file, dpi=100)
    plt.close()
    return image_file


def _plot_simple(
    field_key,
    main_color,
    label,
):
    timeseries = lk_data.get_timeseries()
    date_id = timex.format_time(timeseries[-1]['unixtime'], '%Y%m%d')
    date = timex.format_time(timeseries[-1]['unixtime'], '%Y-%m-%d')

    x = list(map(
        lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
        timeseries[-DAYS_TO_PLOT:],
    ))
    y = list(map(
        lambda d: d[field_key],
        timeseries[-DAYS_TO_PLOT:],
    ))
    plt.plot(x, y, color=main_color)

    plt.title('%s (as of %s)' % (label, date))
    plt.suptitle(
        'Data: https://github.com/CSSEGISandData/COVID-19; '
        + 'https://www.hpb.health.gov.lk/api/get-current-statistical; '
        + 'https://github.com/owid/covid-19-data',
        fontsize=8,
    )

    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(
        tkr.FuncFormatter(lambda x, p: format(int(x), ','))
    )

    fig = plt.gcf()
    fig.autofmt_xdate()
    fig.set_size_inches(12, 6.75)
    image_file = '/tmp/covid19.plot.%s.%s.simple.png' % (
        date_id,
        field_key,
    )
    fig.savefig(image_file, dpi=100)
    plt.close()
    return image_file


def _draw_profile_image_with_stat():
    timeseries = lk_data.get_timeseries()
    latest_item = timeseries[-1]
    date_id = timex.format_time(latest_item['unixtime'], '%Y%m%d')

    stat = latest_item['cum_people_fully_vaccinated'] / POPULATION
    stat_text = '{:.1%}'.format(stat)
    color = 'green'
    subtitle = 'Fully Vaccinated'

    im = Image.open(BASE_IMAGE_FILE)
    im_color = Image.new("RGB", im.size, (255, 255, 255))
    im_color.paste(im)

    width, height = im_color.size
    dim = min(width, height)
    im_cropped = im_color.crop((0, 0, dim, dim))
    # im_cropped.show()

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
    profile_image_file = '/tmp/covid19.image.profile.%s.png' % (
        date_id,
    )
    im_cropped.save(profile_image_file)
    return profile_image_file


def _plot_south_asia(field_key, label, _format):
    jhu_data = covid_data.load_jhu_data()
    country_meta_datas = [
        {'alpha_2': 'IN', 'color': 'orange'},
        {'alpha_2': 'LK', 'color': 'red'},
        {'alpha_2': 'PK', 'color': 'lightgreen'},
        {'alpha_2': 'BD', 'color': 'darkgreen'},
        {'alpha_2': 'NP', 'color': 'blue'},
        {'alpha_2': 'AF', 'color': 'lightblue'},
    ]

    legend_labels = []
    max_last_y = None
    max_last_y_country = None
    for country_meta_data in country_meta_datas:
        country_id = country_meta_data['alpha_2']
        country_data = jhu_data[country_id]
        legend_labels.append(country_data['country_name'])
        timeseries = country_data['timeseries']
        population = country_data['population']

        x = list(map(
            lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
            timeseries[-DAYS_TO_PLOT:],
        ))
        y = list(map(
            lambda d: 100_000 * d[field_key] / population,
            timeseries[(-DAYS_TO_PLOT - MOVING_AVG_WINDOW + 1):],
        ))
        y = np.convolve(
            y,
            np.ones(MOVING_AVG_WINDOW) / MOVING_AVG_WINDOW,
            'valid',
        )
        last_y = y[-1]
        if not max_last_y or last_y > max_last_y:
            max_last_y = last_y
            max_last_y_country = country_id
        plt.plot(x, y, color=country_meta_data['color'])

    plt.title(
        '%s (%d-day Moving Avg.) per 100,000 people in South Asia.' % (
            label,
            MOVING_AVG_WINDOW,
        ),
    )
    plt.suptitle(
        'Data: https://github.com/CSSEGISandData/COVID-19; '
        + 'https://github.com/owid/covid-19-data',
        fontsize=8,
    )
    plt.legend(
        legend_labels,
        loc='upper left',
    )

    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(
        tkr.FuncFormatter(_format)
    )

    fig = plt.gcf()
    fig.autofmt_xdate()
    fig.set_size_inches(8, 4.5)
    image_file = '/tmp/covid19.image.south_asia.%s.png' % field_key
    fig.savefig(image_file, dpi=600)
    plt.close()
    return image_file, max_last_y_country
