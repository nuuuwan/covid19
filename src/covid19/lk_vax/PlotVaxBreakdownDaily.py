import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from infographics import Figure, Infographic

from covid19.lk_vax import epid

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
            # 'new_covishield_dose1',
            # 'new_covishield_dose2',
            # 'new_sinopharm_dose1',
            # 'new_sinopharm_dose2',
            'new_sputnik_dose1',
            'new_sputnik_dose2',
            # 'new_pfizer_dose1',
            # 'new_pfizer_dose2',
            # 'new_moderna_dose1',
            # 'new_moderna_dose2',
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
        y_prev = None
        for y in ys:
            if y_prev:
                plt.bar(x, y, bottom=y_prev)
                y_prev = list(
                    map(lambda i: y_prev[i] + y[i], range(0, len(y)))
                )
            else:
                plt.bar(x, y)
                y_prev = y
        plt.legend(
            [
                # 'Covishield (Dose 1)',
                # 'Covishield (Dose 2)',
                # 'Sinopharm (Dose 1)',
                # 'Sinopharm (Dose 2)',
                'Sputnik (Dose 1)',
                'Sputnik (Dose 2)',
                # 'Pfizer (Dose 1)',
                # 'Pfizer (Dose 2)',
                # 'Moderna (Dose 1)',
                # 'Moderna (Dose 2)',
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

    image_file = '/tmp/covid19.plot.%s.vax_breakdown_daily.png' % (date_id)
    Infographic.Infographic(
        title='Vaccine Type and Dose (Daily)',
        subtitle='Daily COVID19 Vaccinations in Sri Lanka (as of %s)' % date,
        footer_text='\n'.join(
            ['Data from https://www.epid.gov.lk', 'Visualization by @nuuuwan']
        ),
        children=[plot],
    ).save(image_file)
    return image_file


if __name__ == '__main__':
    _plot()
