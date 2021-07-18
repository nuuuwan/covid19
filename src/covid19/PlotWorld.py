import datetime
import random

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np
import pycountry_convert
from infographics import Figure, Infographic

from covid19 import covid_data

MW = 7
DAYS_PLOT = 90
POPULATION = 21_800_000
PADDING = 0.12
Q_PEOPLE = 100_000
random.seed(1)


def _place_id_to_name(continent_id):
    return {
        'LK': 'Sri Lanka',
        'IN': 'India',
        'CN': 'China',
        'US': 'USA',
        'AS': 'Asia (Rest of)',
        'EU': 'Europe',
        'NA': 'North America (Rest of)',
        'SA': 'South America',
        'AF': 'Africa',
        'OC': 'Oceania',
        'U-': '(Unknown)',
    }.get(continent_id, continent_id)


def _func_country_to_continent(country_alpha_2):
    if country_alpha_2 in ['LK', 'IN', 'CN', 'US']:
        return country_alpha_2

    try:
        return pycountry_convert.country_alpha2_to_continent_code(
            country_alpha_2
        )

    except KeyError:
        return None


class PlotWorld(Figure.Figure):
    def __init__(
        self,
        left_bottom=(PADDING, PADDING),
        width_height=(1 - PADDING * 2, 1 - PADDING * 2),
        figure_text='',
        field_key='',
        func_country_to_group=_func_country_to_continent,
    ):
        super().__init__(
            left_bottom=left_bottom,
            width_height=width_height,
            figure_text=figure_text,
        )
        self.field_key = field_key
        self.func_country_to_group = func_country_to_group
        PlotWorld.__prep_data__(self)

    def __prep_data__(self):
        jhu_data = covid_data.load_jhu_data()
        date = jhu_data['LK']['timeseries'][-1]['date'][:10]
        date_id = date.replace('-', '')

        group_to_ut_to_stat = {}
        group_to_date_to_pop = {}
        all_uts = set()
        for country_alpha_2, country_data in jhu_data.items():
            group_id = self.func_country_to_group(country_alpha_2)
            if group_id is None:
                continue

            pop = country_data['population']
            if country_alpha_2 == 'TW':
                pop = 23_861_476

            if pop < 1_000_000:
                continue

            if group_id not in group_to_ut_to_stat:
                group_to_ut_to_stat[group_id] = {}
                group_to_date_to_pop[group_id] = {}
            for item in country_data['timeseries']:
                ut = item['unixtime']
                all_uts.add(ut)
                if ut not in group_to_ut_to_stat[group_id]:
                    group_to_ut_to_stat[group_id][ut] = 0
                    group_to_date_to_pop[group_id][ut] = 0

                stat = item.get(self.field_key, 0)
                group_to_ut_to_stat[group_id][ut] += stat
                group_to_date_to_pop[group_id][ut] += pop

        all_uts = sorted(list(all_uts))[350:]
        x = list(
            map(
                lambda ut: datetime.datetime.fromtimestamp(ut),
                all_uts,
            )
        )
        if 'new' in self.field_key:
            x = x[MW - 1 :]
        group_to_y = {}
        for group_id, date_to_stat in group_to_ut_to_stat.items():
            date_to_pop = group_to_date_to_pop[group_id]
            y = list(
                map(
                    lambda ut: Q_PEOPLE
                    * date_to_stat.get(ut, 0)
                    / date_to_pop.get(ut, 1),
                    all_uts,
                )
            )
            if 'new' in self.field_key:
                y = np.convolve(
                    y,
                    np.ones(MW) / MW,
                    'valid',
                )
            group_to_y[group_id] = y
        group_to_y = dict(sorted(group_to_y.items(), key=lambda x: -x[1][-1]))

        self.__data__ = (
            date,
            date_id,
            x,
            group_to_y,
        )

    def draw(self):
        super().draw()

        (
            date,
            date_id,
            x,
            group_to_y,
        ) = self.__data__

        ax = plt.axes(self.left_bottom + self.width_height)

        for i, (group_id, y) in enumerate(group_to_y.items()):
            color = 'red' if (group_id == 'LK') else 'lightgray'
            plt.plot(x, y, color=color)
            r = (i * 10) % 7 + 1
            plt.text(x[-r], y[-r], _place_id_to_name(group_id), fontsize=12)

        ax.grid()
        ax.get_yaxis().set_major_formatter(
            tkr.FuncFormatter(lambda x, p: format(int(x), ','))
        )
        fig = plt.gcf()
        fig.autofmt_xdate()


def _plot(field_key, label):
    plot = PlotWorld(
        field_key=field_key,
    )
    (
        date,
        date_id,
        x,
        group_to_y,
    ) = plot.get_data()

    image_file = '/tmp/covid19.plot.world.%s.%s.png' % (field_key, date_id)
    Infographic.Infographic(
        title='{label} per {Q_PEOPLE:,} people'.format(
            label=label, Q_PEOPLE=Q_PEOPLE
        ),
        subtitle='COVID19: Sri Lanka (Red) vs. Worldwide (as of %s)' % date,
        footer_text='\n'.join(
            [
                'Data from https://github.com/CSSEGISandData/COVID-19; ',
                'https://github.com/owid/covid-19-data; ',
                'Visualization by @nuuuwan',
            ]
        ),
        children=[plot],
    ).save(image_file)
    return (
        image_file,
        group_to_y,
    )
