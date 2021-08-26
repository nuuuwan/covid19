import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from infographics import Figure, Infographic
from utils import timex

from covid19.lk_vax import epid

BASE_IMAGE_FILE = 'src/covid19/assets/lk_map.png'
FONT_FILE = 'src/covid19/assets/Arial.ttf'

POPULATION = 21_800_000
PADDING = 0.12
WINDOW_DAYS_AND_COLOR = [(7, 'green'), (28, 'orange'), (112, 'red')]


class PlotVaxProjection(Figure.Figure):
    def __init__(
        self,
        left_bottom=(PADDING, PADDING),
        width_height=(1 - PADDING * 2, 1 - PADDING * 2),
        figure_text='',
    ):
        super().__init__(
            left_bottom=left_bottom,
            width_height=width_height,
            figure_text=figure_text,
        )
        self.__data__ = PlotVaxProjection.__prep_data__(self)

    def __prep_data__(self):
        timeseries = epid.load_timeseries()
        last_item = timeseries[-1]
        date = last_item['date']
        last_ut = timex.parse_time(date, '%Y-%m-%d')
        date_id = timex.get_date_id(last_ut)

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
        y = list(
            map(
                lambda d: d['cum_total'] / (POPULATION * 4 / 3),
                timeseries,
            )
        )
        last_cum_total_dose2 = y[-1]
        MAX_PROJECTION_DAYS = 1000
        x_proj = [
            datetime.datetime.fromtimestamp(last_ut + i * timex.SECONDS_IN.DAY)
            for i in range(0, MAX_PROJECTION_DAYS)
        ]
        window_data = []
        for (window_days, color) in WINDOW_DAYS_AND_COLOR:
            rate = (
                (y[-1] - y[-1 - window_days])
                / (t[-1] - t[-1 - window_days])
                * timex.SECONDS_IN.DAY
            )
            y_proj = [
                last_cum_total_dose2 + rate * i
                for i in range(0, MAX_PROJECTION_DAYS)
            ]
            y_proj_filtered = list(
                filter(
                    lambda y: y < 1,
                    y_proj,
                )
            )
            x_proj_filtered = x_proj[: len(y_proj_filtered)]
            days_to_goal = (1 - last_cum_total_dose2) / rate
            goal_ut = last_ut + days_to_goal * timex.SECONDS_IN.DAY

            window_data.append(
                (
                    window_days,
                    color,
                    rate,
                    x_proj_filtered,
                    y_proj_filtered,
                    days_to_goal,
                    goal_ut,
                )
            )

        return (date, date_id, x, y, window_data)

    def draw(self):
        super().draw()

        (date, date_id, x, y, window_data) = self.__data__

        ax = plt.axes(self.left_bottom + self.width_height)
        plt.plot(x, y, color='green')
        legend_items = ['Actual Vaccinations']

        for (
            window_days,
            color,
            rate,
            x_proj_filtered,
            y_proj_filtered,
            days_to_goal,
            goal_ut,
        ) in window_data:
            plt.plot(
                x_proj_filtered,
                y_proj_filtered,
                color=color,
                linestyle='dashed',
            )
            plt.text(
                x_proj_filtered[-1],
                y_proj_filtered[-1],
                timex.format_time(goal_ut, '%b %d,\n%Y'),
                color=color,
                fontsize=8,
                ha='center',
                va='bottom',
            )
            legend_items.append(
                'Projection (based on %d-day rate)' % window_days
            )
        plt.legend(
            legend_items,
            loc='lower right',
        )
        plt.ylabel('Progress to Goal (Vaccinate everyone over the age of 20)')
        plt.grid()
        ax.get_yaxis().set_major_formatter(
            tkr.FuncFormatter(lambda x, p: format(float(x), ',.1%'))
        )

    def get_data(self):
        return self.__data__


def _plot(is_banner_image=False):
    plot = PlotVaxProjection()
    (date, date_id, x, y, window_data) = plot.get_data()

    size = (16, 9)
    banner_label = ''
    if is_banner_image:
        size = (27, 9)
        banner_label = '.banner'

    image_file = '/tmp/covid19.plot.%s.vax_projection%s.png' % (
        date_id,
        banner_label,
    )
    Infographic.Infographic(
        title='Progress to Goal and Projections',
        subtitle='COVID19 Vaccinations in Sri Lanka (as of %s)' % date,
        footer_text='\n'.join(
            ['Data from https://www.epid.gov.lk', 'Visualization by @nuuuwan']
        ),
        children=[plot],
        size=size,
    ).save(image_file)
    return image_file


if __name__ == '__main__':
    _plot(is_banner_image=False)
    _plot(is_banner_image=True)
