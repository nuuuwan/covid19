"""Example 10."""

import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from PIL import Image, ImageDraw, ImageFont
from utils import timex

from covid19 import epid
from covid19._utils import log

BASE_IMAGE_FILE = 'src/covid19/assets/lk_map.png'
FONT_FILE = 'src/covid19/assets/Arial.ttf'

POPULATION = 21_800_000


def _plot_vax_breakdown():
    timeseries = epid.load_timeseries()
    last_item = timeseries[-1]
    date_id = timex.format_time(last_item['ut'], '%Y%m%d')
    date = last_item['date']

    x = list(
        map(
            lambda d: datetime.datetime.fromtimestamp(d['ut']),
            timeseries,
        )
    )
    ys = []
    colors = []
    for (k, color) in [
        ('cum_covishield_dose1', 'blue'),
        ('cum_covishield_dose2', 'purple'),
        ('cum_sinopharm_dose1', 'orange'),
        ('cum_sinopharm_dose2', 'red'),
        ('cum_sputnik_dose1', 'lightgreen'),
        ('cum_sputnik_dose2', 'green'),
        ('cum_pfizer_dose1', 'yellow'),
    ]:
        y = list(
            map(
                lambda d: d[k],
                timeseries,
            )
        )
        ys.append(y)
        colors.append(color)
    plt.stackplot(x, ys, colors=colors)

    plt.title('COVID19 Vaccinations in Sri Lanka (as of %s)' % (date,))
    plt.suptitle(
        'Data: https://www.epid.gov.lk',
        fontsize=6,
    )
    plt.legend(
        [
            'Covishield Dose 1',
            'Covishield Dose 2',
            'Sinopharm Dose 1',
            'Sinopharm Dose 2',
            'Sputnik Dose 1',
            'Sputnik Dose 2',
            'Pfizer',
        ],
        loc='upper left',
    )

    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(
        tkr.FuncFormatter(lambda x, p: format(float(x), ',.0f'))
    )
    fig = plt.gcf()
    fig.autofmt_xdate()
    fig.set_size_inches(16, 9)
    image_file = '/tmp/covid19.plot.%s.vax_breakdown.png' % (date_id)
    fig.savefig(image_file, dpi=200)
    plt.close()
    log.info('Saved image to %s', image_file)
    return image_file


def _plot_vax_summary():
    timeseries = epid.load_timeseries()
    last_item = timeseries[-1]
    date_id = timex.format_time(last_item['ut'], '%Y%m%d')
    date = last_item['date']

    x = list(
        map(
            lambda d: datetime.datetime.fromtimestamp(d['ut']),
            timeseries,
        )
    )
    y1 = list(
        map(
            lambda d: d['cum_total_dose1'] - d['cum_total_dose2'],
            timeseries,
        )
    )
    y2 = list(
        map(
            lambda d: d['cum_total_dose2'],
            timeseries,
        )
    )
    plt.stackplot(x, [y2, y1], colors=['green', 'orange'])

    plt.title(
        'COVID19 Vaccinations in Sri Lanka by Vaccine (as of %s)' % (date,)
    )
    plt.suptitle(
        'Data: https://www.epid.gov.lk',
        fontsize=6,
    )
    plt.legend(
        [
            'Fully vaccinated',
            'Partially Vaccinated (1 dose)',
        ],
        loc='upper left',
    )

    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(
        tkr.FuncFormatter(lambda x, p: format(float(x), ',.0f'))
    )
    fig = plt.gcf()
    fig.autofmt_xdate()
    fig.set_size_inches(16, 9)
    image_file = '/tmp/covid19.plot.%s.vax_summary.png' % (date_id)
    fig.savefig(image_file, dpi=200)
    plt.close()
    log.info('Saved image to %s', image_file)
    return image_file


def _plot_vax_proj():
    timeseries = epid.load_timeseries()
    last_item = timeseries[-1]

    last_ut = last_item['ut']
    date_id = timex.format_time(last_ut, '%Y%m%d')
    date = last_item['date']

    t = list(
        map(
            lambda d: d['ut'],
            timeseries,
        )
    )
    x = list(
        map(
            lambda ti: datetime.datetime.fromtimestamp(ti),
            t,
        )
    )
    PROJECTION_DAYS = 1000
    y = list(
        map(
            lambda d: d['cum_total'] / (POPULATION * 4 / 3),
            timeseries,
        )
    )
    last_cum_total_dose2 = y[-1]
    Q = timex.SECONDS_IN.DAY
    rate_14days = (y[-1] - y[-1 - 14]) / (t[-1] - t[-1 - 14]) * Q
    rate_28days = (y[-1] - y[-1 - 28]) / (t[-1] - t[-1 - 28]) * Q
    rate_all = (y[-1] - y[0]) / (t[-1] - t[0]) * Q

    x_proj = [
        datetime.datetime.fromtimestamp(last_ut + i * timex.SECONDS_IN.DAY)
        for i in range(0, PROJECTION_DAYS)
    ]
    y_proj1 = [
        last_cum_total_dose2 + rate_14days * i
        for i in range(0, PROJECTION_DAYS)
    ]
    y_proj1 = list(
        filter(
            lambda y: y < 1,
            y_proj1,
        )
    )
    y_proj2 = [
        last_cum_total_dose2 + rate_28days * i
        for i in range(0, PROJECTION_DAYS)
    ]
    y_proj2 = list(
        filter(
            lambda y: y < 1,
            y_proj2,
        )
    )
    y_proj3 = [
        last_cum_total_dose2 + rate_all * i for i in range(0, PROJECTION_DAYS)
    ]
    y_proj3 = list(
        filter(
            lambda y: y < 1,
            y_proj3,
        )
    )

    plt.plot(x, y, color='green')
    plt.plot(
        x_proj[: len(y_proj1)],
        y_proj1,
        color='green',
        linestyle='dashed',
    )
    plt.plot(
        x_proj[: len(y_proj2)],
        y_proj2,
        color='orange',
        linestyle='dashed',
    )
    plt.plot(
        x_proj[: len(y_proj3)],
        y_proj3,
        color='red',
        linestyle='dashed',
    )

    plt.title(
        'Projected COVID19 Vaccinations in Sri Lanka (as of %s)' % (date,)
    )
    plt.suptitle(
        'Data: https://www.epid.gov.lk',
        fontsize=6,
    )
    plt.legend(
        [
            'Actual Vaccinations',
            'Projection (at current 14-day avg. rate)',
            'Projection (at current 28-day avg. rate)',
            'Projection (at all time rate)',
        ],
        loc='lower right',
    )
    plt.ylabel('Progress to Goal (Vaccinate Population > 20years)')

    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(
        tkr.FuncFormatter(lambda x, p: format(float(x), ',.1%'))
    )
    fig = plt.gcf()
    fig.autofmt_xdate()
    fig.set_size_inches(8, 9)
    image_file = '/tmp/covid19.plot.%s.vax_proj.png' % (date_id)
    fig.savefig(image_file, dpi=400)
    plt.close()
    log.info('Saved image to %s', image_file)
    return image_file


def _draw_profile_image_with_stat():
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


if __name__ == '__main__':
    _plot_vax_proj()
