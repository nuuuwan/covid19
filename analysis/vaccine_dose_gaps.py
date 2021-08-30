import os
import statistics

import matplotlib.pyplot as plt

from utils import timex, tsv

from covid19.lk_vax import epid

VACCINE_TYPE_TO_BOUNDS = {
    'covishield': [8, 12],
    'pfizer': [3, 4],
    'moderna': [4, 12],
    'sputnik': [3, 12],
    'sinopharm': [3, 4],
}


def get_gaps_data():
    timeseries = epid.load_timeseries()
    vaccine_type = 'covishield'

    data_list = []
    for vaccine_type in ['covishield', 'pfizer', 'moderna', 'sputnik', 'sinopharm']:
        dose1_days = []
        dose2_days = []
        for d in timeseries:
            ut = d['ut']
            dose1 = d[f'new_{vaccine_type}_dose1']
            dose2 = d[f'new_{vaccine_type}_dose2']

            dose1_days += [ut for i in range(0, dose1)]
            dose2_days += [ut for i in range(0, dose2)]

        duts = []
        for i_dose2, ut2 in enumerate(dose2_days):
            ut1 = dose1_days[i_dose2]
            dut = (ut2 - ut1) / timex.SECONDS_IN.WEEK
            duts.append(dut)

        data_list.append(dict(
            vaccine_type=vaccine_type,
            mean=statistics.mean(duts),
            stdev=statistics.stdev(duts),
            min=min(duts),
            max=max(duts),
            duts=duts,
        ))

        fig, ax = plt.subplots()
        ax.set_title(f'{vaccine_type} - Weeks between Dose 1 and Dose 2')

        ax.set_ylabel('People with Vaccine')
        ax.set_xlabel('Duration in Weeks')

        N, bins, patches = plt.hist(duts, bins=30, ec='black')
        min_weeks, max_weeks = VACCINE_TYPE_TO_BOUNDS[vaccine_type]
        for i in range(0, len(patches)):
            bin_mean = (bins[i] + bins[i + 1]) * 0.5

            if bin_mean < min_weeks:
                color = 'blue'
            elif bin_mean > max_weeks:
                color = 'red'
            else:
                color = 'green'
            patches[i].set_facecolor(color)

        fig.set_size_inches(16, 9)
        image_file = f'/tmp/covid19.analysis.vaccine_dose_gaps.{vaccine_type}.png'
        fig.savefig(image_file, dpi=300)
        os.system(f'open {image_file}')

    tsv_file = '/tmp/covid19.analysis.vaccine_dose_gaps.tsv'
    tsv.write(tsv_file, data_list)

if __name__ == '__main__':
    get_gaps_data()
