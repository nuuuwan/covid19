from covid19.lk_vax import epid
import statistics
from utils import timex, tsv

if __name__ == '__main__':
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
        ))

    print(data_list)
    tsv_file = '/tmp/vaccine_dose_gaps.tsv'
    tsv.write(tsv_file, data_list)
