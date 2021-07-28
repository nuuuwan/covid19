import datetime
import math
import os

import numpy as np
import matplotlib.pyplot as plt

from covid19 import covid_data

TIME_SPAN = 56
MIN_DEATHS_START = 5
MVN_AVG_WND = 14


def draw_curves():
    jhu_data = covid_data.load_jhu_data()

    dates = [
        datetime.datetime.fromtimestamp(d['unixtime'])
        for d in list(jhu_data.values())[0]['timeseries'][-TIME_SPAN:]
    ]

    country_info_list = []
    for country_alpha_2, country_data in jhu_data.items():
        timeseries = country_data['timeseries']
        deaths = list(
            map(
                lambda item: (int)(item['new_deaths']),
                timeseries[-TIME_SPAN - MVN_AVG_WND + 1:],
            )
        )
        deaths_smooth = np.convolve(
            deaths, np.ones(MVN_AVG_WND) / MVN_AVG_WND, 'valid'
        )
        sum_deaths = sum(deaths_smooth)
        deaths_start = deaths_smooth[0]
        if deaths_start < MIN_DEATHS_START:
            continue

        norm_deaths = [deaths / deaths_start for deaths in deaths_smooth]
        norm_deaths_end = norm_deaths[-1]

        country_info_list.append(dict(
            country_alpha_2=country_alpha_2,
            country_data=country_data,
            norm_deaths_end=norm_deaths_end,
            norm_deaths=norm_deaths,
        ))
    country_info_list = sorted(
        country_info_list,
        key=lambda x: x['norm_deaths_end'],
    )

    ASPECT_RATIO = 9 / 16
    GROUP_COUNT = 4
    n_countries = len(country_info_list)
    countries_per_group = math.ceil(n_countries / GROUP_COUNT)
    n_cols = math.ceil(math.sqrt(countries_per_group / ASPECT_RATIO))
    n_rows = math.ceil(countries_per_group / n_cols)

    for i in range(0, GROUP_COUNT):
        figure, axis = plt.subplots(n_cols, n_rows)
        i_col, i_row = 0, 0
        min_norm_deaths_end = None
        max_norm_deaths_end = None
        for j in range(0, countries_per_group):
            i_info  = i * countries_per_group + j
            if i_info >= n_countries:
                break
            data = country_info_list[i_info]
            ax = axis[i_col, i_row]
            norm_deaths = data['norm_deaths']
            norm_deaths_end = data['norm_deaths_end']
            if not min_norm_deaths_end:
                min_norm_deaths_end = norm_deaths_end
            max_norm_deaths_end = norm_deaths_end

            if norm_deaths_end > 1.5:
                color = 'red'
            elif norm_deaths_end < 0.667:
                color = 'green'
            else:
                color = 'orange'

            ax.plot(dates, norm_deaths, color=color)
            ax.get_xaxis().set_visible(False)
            title = '%s - %4.1fx' % (data['country_data']['country_name'], data['norm_deaths_end'])
            ax.set_title(title)

            i_col += 1
            if i_col == n_cols:
                i_col = 0
                i_row += 1

        label = "%4.1fx to %4.1fx of daily deaths (%d-day avg) as of %d days ago" % (min_norm_deaths_end, max_norm_deaths_end, MVN_AVG_WND, TIME_SPAN)
        plt.suptitle('COVID19 Curves - %s' % label)
        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        image_file = '/tmp/covid19.adhoc3_curves.group%0d.png' % i
        fig.savefig(image_file, dpi=100)
        os.system('open %s' % image_file)
        plt.close()



if __name__ == '__main__':
    draw_curves()
