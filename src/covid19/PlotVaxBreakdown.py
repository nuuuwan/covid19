import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from infographics import Figure, Infographic

from covid19 import epid

BASE_IMAGE_FILE = 'src/covid19/assets/lk_map.png'
FONT_FILE = 'src/covid19/assets/Arial.ttf'

POPULATION = 21_800_000
PADDING = 0.12


class PlotVaxBreakdown(Figure.Figure):
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
        self.__data__ = PlotVaxBreakdown.__prep_data__(self)

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
        ys = []
        for k in [
            'cum_covishield_dose1',
            'cum_covishield_dose2',
            'cum_sinopharm_dose1',
            'cum_sinopharm_dose2',
            'cum_sputnik_dose1',
            'cum_sputnik_dose2',
            'cum_pfizer_dose1',
            'cum_moderna_dose1',
        ]:
            y = list(
                map(
                    lambda d: d[k],
                    timeseries,
                )
            )
            ys.append(y)
        return (x, ys, date, date_id)

    def draw(self):
        super().draw()

        (x, ys, date, date_id) = self.__data__

        ax = plt.axes(self.left_bottom + self.width_height)
        plt.stackplot(x, ys)
        plt.legend(
            [
                'Covishield (Dose 1)',
                'Covishield (Dose 2)',
                'Sinopharm (Dose 1)',
                'Sinopharm (Dose 2)',
                'Sputnik (Dose 1)',
                'Sputnik (Dose 2)',
                'Pfizer (Dose 1)',
                'Moderna (Dose 1)',
            ],
            loc='upper left',
        )

        ax.grid()
        ax.get_yaxis().set_major_formatter(
            tkr.FuncFormatter(lambda x, p: format(float(x), ',.0f'))
        )
        fig = plt.gcf()
        fig.autofmt_xdate()

    def get_data(self):
        return self.__data__


def _plot():
    plot = PlotVaxBreakdown()
    (x, ys, date, date_id) = plot.get_data()

    image_file = '/tmp/covid19.plot.%s.vax_breakdown.png' % (date_id)
    Infographic.Infographic(
        title='Vaccine Type and Dose',
        subtitle='COVID19 Vaccinations in Sri Lanka (as of %s)' % date,
        footer_text='\n'.join(
            ['Data from https://www.epid.gov.lk', 'Visualization by @nuuuwan']
        ),
        children=[plot],
    ).save(image_file)
    return image_file


if __name__ == '__main__':
    _plot()
