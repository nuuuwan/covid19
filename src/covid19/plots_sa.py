"""Example 10."""

import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np

from covid19 import covid_data

BASE_IMAGE_FILE = 'src/covid19/assets/lk_map.png'
FONT_FILE = 'src/covid19/assets/Arial.ttf'

DAYS_PLOT = 90
MW = 7
POPULATION = 21_800_000


def _plot_south_asia(field_key, label, _format):
    moving_avg_window = MW \
        if (field_key != 'cum_people_fully_vaccinated') \
        else 1
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
            timeseries[-DAYS_PLOT:],
        ))
        y = list(map(
            lambda d: 100_000 * d[field_key] / population,
            timeseries[(-DAYS_PLOT - moving_avg_window + 1):],
        ))
        y = np.convolve(
            y,
            np.ones(moving_avg_window) / moving_avg_window,
            'valid',
        )
        last_y = y[-1]
        if not max_last_y or last_y > max_last_y:
            max_last_y = last_y
            max_last_y_country = country_id
        plt.plot(x, y, color=country_meta_data['color'])

    moving_avg_label = ' (%d-Day Moving Avg.)' % moving_avg_window \
        if (moving_avg_window > 1) \
        else ''
    plt.title(
        '%s%s per 100,000 people in South Asia.' % (
            label,
            moving_avg_label,
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
