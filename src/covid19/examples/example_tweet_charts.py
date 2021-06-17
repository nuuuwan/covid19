"""Example 10."""

import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np

from covid19 import lk_data

DAYS_TO_PLOT = 56
MOVING_AVG_WINDOW = 7


def _plot_with_time_window(
    field_key,
    main_color,
    sub_color,
    label,
):
    timeseries = lk_data.get_timeseries()
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
        '%s with a %d-day moving average.' % (
            label,
            MOVING_AVG_WINDOW,
        ),
    )
    plt.suptitle(
        'Data Source: https://github.com/CSSEGISandData/COVID-19 '
        + '& https://www.hpb.health.gov.lk/api/get-current-statistical',
        fontsize=6,
    )

    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(
        tkr.FuncFormatter(lambda x, p: format(int(x), ','))
    )

    fig = plt.gcf()
    fig.autofmt_xdate()
    fig.set_size_inches(12, 6.75)
    fig.savefig(
        '/tmp/example_tweet.%s.png' % (field_key),
        dpi=100,
    )

    plt.show()


def _plot_simple(
    field_key,
    main_color,
    label,
):
    timeseries = lk_data.get_timeseries()

    x = list(map(
        lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
        timeseries[-DAYS_TO_PLOT:],
    ))
    y = list(map(
        lambda d: d[field_key],
        timeseries[-DAYS_TO_PLOT:],
    ))
    plt.plot(x, y, color=main_color)

    plt.title('%s.' % (label))
    plt.suptitle(
        'Data Source: https://github.com/CSSEGISandData/COVID-19 '
        + '& https://www.hpb.health.gov.lk/api/get-current-statistical',
        fontsize=6,
    )

    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(
        tkr.FuncFormatter(lambda x, p: format(int(x), ','))
    )

    fig = plt.gcf()
    fig.autofmt_xdate()
    fig.set_size_inches(12, 6.75)
    fig.savefig(
        '/tmp/example_tweet.simple.%s.png' % (field_key),
        dpi=100,
    )

    plt.show()


if __name__ == '__main__':
    # field_key = 'new_deaths'
    # main_color = 'red'
    # sub_color = 'pink'
    # label = 'Daily COVID19 Deaths'

    # field_key = 'active'
    # main_color = 'blue'
    # sub_color = 'lightblue'
    # label = 'Active COVID19 Cases'

    # _plot_simple('active', 'blue', 'Active COVID19 Cases')
    # _plot_with_time_window('new_deaths', 'red', 'pink', 'Daily COVID19 Deaths')
    # _plot_with_time_window('new_pcr_tests', 'orange', (1, 0.9, 0.8), 'Daily COVID19 PCR Tests')
    _plot_with_time_window('new_vaccinations', 'green', 'lightgreen', 'Daily COVID19 Vaccinations')
