import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from infographics import Figure, Infographic

from covid19.lk_vax import epid

BASE_IMAGE_FILE = 'src/covid19/assets/lk_map.png'
FONT_FILE = 'src/covid19/assets/Arial.ttf'

POPULATION = 21_800_000
PADDING = 0.12


class PlotVaxSummary(Figure.Figure):
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
        self.__data__ = PlotVaxSummary.__prep_data__(self)

    def __prep_data__(self):
        timeseries = epid.load_timeseries()
        last_item = timeseries[-1]
        date = last_item['date']
        date_id = date.replace('-', '')

        x = list(
            map(
                lambda d: datetime.datetime.fromtimestamp(d['ut']),
                timeseries,
            )
        )
        y_partial = list(
            map(
                lambda d: (d['cum_total_dose1'] - d['cum_total_dose2'])
                / POPULATION,
                timeseries,
            )
        )
        y_full = list(
            map(
                lambda d: d['cum_total_dose2'] / POPULATION,
                timeseries,
            )
        )
        return (x, [y_full, y_partial], date, date_id)

    def draw(self):
        super().draw()

        (x, ys, date, date_id) = self.__data__

        ax = plt.axes(self.left_bottom + self.width_height)
        plt.stackplot(x, ys)
        plt.legend(
            [
                'Fully Vaccinated (2 Doses)',
                'Partially Vaccinated (1 Dose)',
            ],
            loc='upper left',
        )
        plt.ylabel('Proportion of Total Population')
        ax.grid()
        ax.get_yaxis().set_major_formatter(
            tkr.FuncFormatter(lambda x, p: format(float(x), '.1%'))
        )
        fig = plt.gcf()
        fig.autofmt_xdate()

    def get_data(self):
        return self.__data__


def _plot():
    plot = PlotVaxSummary()
    (x, ys, date, date_id) = plot.get_data()

    image_file = '/tmp/covid19.plot.%s.vax_summary.png' % (date_id)
    Infographic.Infographic(
        title='Fully and Partially Vaccinated Population',
        subtitle='COVID19 Vaccinations in Sri Lanka (as of %s)' % date,
        footer_text='\n'.join(
            ['Data from https://www.epid.gov.lk', 'Visualization by @nuuuwan']
        ),
        children=[plot],
    ).save(image_file)
    return image_file


if __name__ == '__main__':
    _plot()
