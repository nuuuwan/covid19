import os
import statistics

import matplotlib.pyplot as plt

from utils import timex, tsv

from covid19.lk_vax import epid


def get_gaps_data():
    ut_now = timex.get_unixtime()
    timeseries = epid.load_timeseries()
    vaccine_type = 'covishield'

    data_list = []
    for vaccine_type in [
        'covishield',
        'pfizer',
        'moderna',
        'sputnik',
        'sinopharm',
    ]:
        dose1_days = []
        dose2_days = []
        for d in timeseries:
            ut = d['ut']
            dose1 = d[f'new_{vaccine_type}_dose1']
            dose2 = d[f'new_{vaccine_type}_dose2']

            dose1_days += [ut for i in range(0, dose1)]
            dose2_days += [ut for i in range(0, dose2)]

        duts = []
        n_dose1 = len(dose1_days)
        n_dose2 = len(dose2_days)
        for i in range(0, n_dose2):
            ut2 = dose2_days[i]
            ut1 = dose1_days[i]
            dut = (ut2 - ut1) / timex.SECONDS_IN.WEEK
            duts.append(dut)

        duts_no = []
        for i in range(0, n_dose1 - n_dose2):
            ut1 = dose1_days[n_dose2 + i]
            dut = (ut_now - ut1) / timex.SECONDS_IN.WEEK
            duts_no.append(dut)

        data_list.append(
            dict(
                vaccine_type=vaccine_type,
                mean=statistics.mean(duts),
                stdev=statistics.stdev(duts),
                min=min(duts),
                max=max(duts),
                duts=duts,
            )
        )

        fig, ax = plt.subplots()
        ax.set_title(f'{vaccine_type} - Weeks between Dose 1 and Dose 2')

        ax.set_ylabel('People with Vaccine')
        ax.set_xlabel('Duration in Weeks')

        plt.hist(duts, color='blue', ec='black')
        # plt.hist(duts_no, color='red', ec='black')
        fig.set_size_inches(16, 9)
        image_file = (
            f'/tmp/covid19.analysis.vaccine_dose_gaps.{vaccine_type}.png'
        )
        fig.savefig(image_file, dpi=300)
        os.system(f'open {image_file}')

    tsv_file = '/tmp/covid19.analysis.vaccine_dose_gaps.tsv'
    tsv.write(tsv_file, data_list)


if __name__ == '__main__':
    get_gaps_data()
