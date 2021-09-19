import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np
from infographics import Figure, Infographic

from covid19 import covid_data

MW = 7
DAYS_PLOT = 90
POPULATION = 21_800_000
PADDING = 0.12
Q_PEOPLE = 100_000

COUNTRY_META_DATAS = [
    {'alpha_2': 'IN', 'color': 'orange'},
    {'alpha_2': 'LK', 'color': 'red'},
    {'alpha_2': 'PK', 'color': 'lightgreen'},
    {'alpha_2': 'BD', 'color': 'darkgreen'},
    {'alpha_2': 'NP', 'color': 'blue'},
    {'alpha_2': 'AF', 'color': 'lightblue'},
]


class PlotSouthAsia(Figure.Figure):
    def __init__(
        self,
        left_bottom=(PADDING, PADDING),
        width_height=(1 - PADDING * 2, 1 - PADDING * 2),
        figure_text='',
        field_key='new_confirmed',
    ):
        super().__init__(
            left_bottom=left_bottom,
            width_height=width_height,
            figure_text=figure_text,
        )
        self.field_key = field_key
        PlotSouthAsia.__prep_data__(self)

    def __prep_data__(self):
        moving_avg_window = (
            MW if (self.field_key != 'cum_people_fully_vaccinated') else 1
        )
        jhu_data = covid_data.load_jhu_data()
        date = jhu_data['LK']['timeseries'][-1]['date'][:10]
        date_id = date.replace('-', '')

        legend_labels = []
        max_last_y = None
        max_last_y_country = None
        country_to_data = {}
        for country_meta_data in COUNTRY_META_DATAS:
            country_id = country_meta_data['alpha_2']
            country_data = jhu_data[country_id]
            legend_labels.append(country_data['country_name'])
            timeseries = country_data['timeseries']
            population = country_data['population']

            x = list(
                map(
                    lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
                    timeseries[-DAYS_PLOT:],
                )
            )
            y = list(
                map(
                    lambda d: Q_PEOPLE * d[self.field_key] / population,
                    timeseries[(-DAYS_PLOT - moving_avg_window + 1):],
                )
            )
            y = np.convolve(
                y,
                np.ones(moving_avg_window) / moving_avg_window,
                'valid',
            )

            country_to_data[country_id] = (x, y, country_meta_data['color'])

            last_y = y[-1]
            if not max_last_y or last_y > max_last_y:
                max_last_y = last_y
                max_last_y_country = country_id
        self.__data__ = (
            date,
            date_id,
            country_to_data,
            legend_labels,
            max_last_y,
            max_last_y_country,
        )

    def draw(self):
        super().draw()

        (
            date,
            date_id,
            country_to_data,
            legend_labels,
            max_last_y,
            max_last_y_country,
        ) = self.__data__

        ax = plt.axes(self.left_bottom + self.width_height)

        for country_id, (x, y, color) in country_to_data.items():
            plt.plot(x, y, color=color)

        if self.field_key == 'new_deaths':

            def func_format(x, p):
                return format(float(x), '.1f')

        else:

            def func_format(x, p):
                return format(int(x), ',')

        plt.legend(legend_labels)
        ax.grid()
        ax.get_yaxis().set_major_formatter(tkr.FuncFormatter(func_format))
        fig = plt.gcf()
        fig.autofmt_xdate()


def _plot(field_key, label):
    moving_avg_window = (
        MW if (field_key != 'cum_people_fully_vaccinated') else 1
    )
    plot = PlotSouthAsia(
        field_key=field_key,
    )
    (
        date,
        date_id,
        country_to_data,
        legend_labels,
        max_last_y,
        max_last_y_country,
    ) = plot.get_data()

    image_file = '/tmp/covid19.plot.south_asia.%s.%s.png' % (
        field_key,
        date_id,
    )
    Infographic.Infographic(
        title=f'{label} per {Q_PEOPLE:,} people ({moving_avg_window}'
        + ' day moving average)',
        subtitle='COVID19 in South Asia (as of %s)' % date,
        footer_text='\n'.join(
            [
                'Data from https://github.com/CSSEGISandData/COVID-19; ',
                'https://github.com/owid/covid-19-data; ',
                'Visualization by @nuuuwan',
            ]
        ),
        children=[plot],
    ).save(image_file)
    return image_file, max_last_y_country
