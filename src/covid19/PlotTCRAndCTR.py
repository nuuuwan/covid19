import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np
from infographics import Figure, Infographic
from utils import timex

from covid19 import lk_data

DAYS_PLOT = 180
MW = 7
POPULATION = 21_800_000
PADDING = 0.15


class PlotTCRAndCTR(Figure.Figure):
    def __init__(
        self,
        left_bottom=None,
        width_height=((1 - PADDING * 2) / 2, 1 - PADDING * 2),
        figure_text='',
        plot_type='tcr',
    ):
        if left_bottom is None:
            if plot_type != 'tcr':
                left_bottom = (0.5 + PADDING / 2, PADDING)
            else:
                left_bottom = (PADDING, PADDING)

        super().__init__(
            left_bottom=left_bottom,
            width_height=width_height,
            figure_text=figure_text,
        )
        self.plot_type = plot_type
        self.__data__ = PlotTCRAndCTR.__prep_data__(self)

    def __prep_data__(self):
        moving_avg_window = MW
        timeseries = lk_data.get_timeseries()
        date_id = timex.format_time(timeseries[-1]['unixtime'], '%Y%m%d')
        date = timex.format_time(timeseries[-1]['unixtime'], '%Y-%m-%d')

        if self.plot_type != 'tcr':

            def func_y(d):
                return d['new_confirmed'] / d['new_pcr_tests']

        else:

            def func_y(d):
                return d['new_pcr_tests'] / d['new_confirmed']

        x = list(
            map(
                lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
                timeseries[-DAYS_PLOT:],
            )
        )
        y = list(
            map(
                func_y,
                timeseries[-DAYS_PLOT - moving_avg_window + 1:],
            )
        )
        y = np.convolve(
            y,
            np.ones(moving_avg_window) / moving_avg_window,
            'valid',
        )
        return (date_id, date, x, y)

    def draw(self):
        (date_id, date, x, y) = self.__data__

        if self.plot_type != 'tcr':
            format_str = '.1%'
            color = 'orange'
            y_label = 'Cases per Test'
        else:
            format_str = '.1f'
            color = 'green'
            y_label = 'Tests per Case'

        ax = plt.axes(self.left_bottom + self.width_height)
        ax.grid()
        plt.plot(x, y, color=color)
        ax.get_yaxis().set_major_formatter(
            tkr.FuncFormatter(lambda x, p: format(float(x), format_str))
        )
        plt.ylabel(y_label)
        fig = plt.gcf()
        fig.autofmt_xdate()

    def get_data(self):
        return self.__data__


def _plot():
    plot_tcr = PlotTCRAndCTR(plot_type='tcr')
    plot_ctr = PlotTCRAndCTR(plot_type='ctr')
    (date_id, date, x, y) = plot_tcr.get_data()

    image_file = '/tmp/covid19.plot.%s.tcr.png' % (date_id,)
    Infographic.Infographic(
        title=' '.join(
            [
                'Test-to-Case Ratio (TCR) and',
                'Case-to-Test Ratio (%d-Day Moving Avg)' % (MW),
            ]
        ),
        subtitle='COVID19 Testing in Sri Lanka (as of %s)' % date,
        footer_text='\n'.join(
            [
                'Data from https://github.com/CSSEGISandData/COVID-19; ',
                'https://www.hpb.health.gov.lk/api/get-current-statistical; ',
                'https://github.com/owid/covid-19-data;',
                'Visualization by @nuuuwan',
            ]
        ),
        children=[plot_tcr, plot_ctr],
    ).save(image_file)
    return image_file


if __name__ == '__main__':
    _plot()
