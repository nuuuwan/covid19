import statistics

import scipy.stats
from utils import tsv

from covid19 import covid_data

WINDOW_DAYS = 60
MIN_SUM_DEATHS = 1000


def analyze():
    jhu_data = covid_data.load_jhu_data()

    analysis_data_list = []
    for country_alpha_2, country_data in jhu_data.items():
        country_name = country_data['country_name']
        timeseries = country_data['timeseries']

        deaths = list(
            map(
                lambda item: (int)(item['new_deaths']),
                timeseries[-WINDOW_DAYS:],
            )
        )
        sum_deaths = sum(deaths)
        if sum_deaths < MIN_SUM_DEATHS:
            continue
        mean = statistics.mean(deaths)
        if mean == 0:
            continue
        stdev = statistics.stdev(deaths)
        cov = stdev / mean
        iqr = scipy.stats.iqr(deaths)
        median = statistics.median(deaths)

        if median == 0:
            continue
        iqr_to_median = iqr / median

        analysis_data = dict(
            country_name=country_name,
            sum_deaths=sum_deaths,
            mean=mean,
            stdev=stdev,
            cov=cov,
            median=median,
            iqr=iqr,
            iqr_to_median=iqr_to_median,
        )
        analysis_data_list.append(analysis_data)

    analysis_data_list = sorted(
        analysis_data_list,
        key=lambda analysis_data: analysis_data['cov'],
    )

    analysis_file = '/tmp/covid19.adhoc2_flatness.tsv'
    tsv.write(analysis_file, analysis_data_list)


if __name__ == '__main__':
    analyze()
