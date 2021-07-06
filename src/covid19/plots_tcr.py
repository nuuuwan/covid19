"""Example 10."""

import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np

from utils import timex

from covid19 import lk_data

BASE_IMAGE_FILE = 'src/covid19/assets/lk_map.png'
FONT_FILE = 'src/covid19/assets/Arial.ttf'

DAYS_PLOT = 90
MW = 7
POPULATION = 21_800_000


def _plot_tcr():
    moving_avg_window = MW
    timeseries = lk_data.get_timeseries()
    date_id = timex.format_time(timeseries[-1]['unixtime'], '%Y%m%d')
    date = timex.format_time(timeseries[-1]['unixtime'], '%Y-%m-%d')

    x = list(map(
        lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
        timeseries[-DAYS_PLOT:],
    ))
    y = list(map(
        lambda d: d['new_pcr_tests'] / d['new_confirmed'],
        timeseries[-DAYS_PLOT-moving_avg_window + 1:],
    ))
    y = np.convolve(
        y,
        np.ones(moving_avg_window) / moving_avg_window,
        'valid',
    )
    plt.plot(x, y, color='green')

    plt.title('Test-to-Case Ratio (TCR) %d-Day Moving Avg. as of %s' % (
        moving_avg_window,
        date,
    ))
    plt.suptitle(
        'Data: https://github.com/CSSEGISandData/COVID-19; '
        + 'https://www.hpb.health.gov.lk/api/get-current-statistical; '
        + 'https://github.com/owid/covid-19-data',
        fontsize=8,
    )

    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(
        tkr.FuncFormatter(lambda x, p: format(float(x), '.1f'))
    )

    fig = plt.gcf()
    fig.autofmt_xdate()
    fig.set_size_inches(8, 9)
    image_file = '/tmp/covid19.plot.%s.tcr.png' % (
        date_id,
    )
    fig.savefig(image_file, dpi=100)
    plt.close()
    return image_file


def _plot_ctr():
    moving_avg_window = MW
    timeseries = lk_data.get_timeseries()
    date_id = timex.format_time(timeseries[-1]['unixtime'], '%Y%m%d')
    date = timex.format_time(timeseries[-1]['unixtime'], '%Y-%m-%d')

    x = list(map(
        lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
        timeseries[-DAYS_PLOT:],
    ))
    y = list(map(
        lambda d: d['new_confirmed'] / d['new_pcr_tests'],
        timeseries[-DAYS_PLOT-moving_avg_window + 1:],
    ))
    y = np.convolve(
        y,
        np.ones(moving_avg_window) / moving_avg_window,
        'valid',
    )
    plt.plot(x, y, color='orange')

    plt.title('Case-to-Test Ratio %d-Day Moving Avg. as of %s' % (
        moving_avg_window,
        date,
    ))
    plt.suptitle(
        'Data: https://github.com/CSSEGISandData/COVID-19; '
        + 'https://www.hpb.health.gov.lk/api/get-current-statistical; '
        + 'https://github.com/owid/covid-19-data',
        fontsize=8,
    )

    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(
        tkr.FuncFormatter(lambda x, p: format(float(x), '.1%'))
    )

    fig = plt.gcf()
    fig.autofmt_xdate()
    fig.set_size_inches(8, 9)
    image_file = '/tmp/covid19.plot.%s.ctr.png' % (
        date_id,
    )
    fig.savefig(image_file, dpi=100)
    plt.close()
    return image_file
