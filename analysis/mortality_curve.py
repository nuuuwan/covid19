from utils import timex, tsv

from covid19.lk_vax import epid

WINDOW = 28
TARGET_POPULATION = 14_600_000


def analysis():
    timeseries = epid.load_timeseries()
    print(len(timeseries))

    latest = timeseries[-1]
    window_ago = timeseries[-1 - WINDOW]
    dose2_per_day = (
        latest['cum_total_dose2'] - window_ago['cum_total_dose2']
    ) / WINDOW
    dose1_per_day = (
        latest['cum_total_dose1'] - window_ago['cum_total_dose1']
    ) / WINDOW

    # projection
    cum_total_dose1 = latest['cum_total_dose1']
    cum_total_dose2 = latest['cum_total_dose2']
    ut = latest['ut']

    mort_unvaxed = 2600
    mort_dose1 = 12_000
    mort_dose2 = 67_000

    data_list = []
    for i_day in range(0, 56):
        ut += timex.SECONDS_IN.DAY
        date = timex.get_date(ut)
        dose1 = min(dose1_per_day, TARGET_POPULATION - cum_total_dose1)
        dose2 = min(
            dose2_per_day,
            TARGET_POPULATION - cum_total_dose2,
            cum_total_dose1 - cum_total_dose2,
        )

        cum_total_dose1 += dose1
        cum_total_dose2 += dose2
        unvaxed = TARGET_POPULATION - cum_total_dose1

        daily_deaths_unvaxed = unvaxed / mort_unvaxed / 7
        daily_deaths_dose1 = (
            (cum_total_dose1 - cum_total_dose2) / mort_dose1 / 7
        )
        daily_deaths_dose2 = cum_total_dose2 / mort_dose2 / 7

        data_list.append(
            dict(
                date=date,
                pop_over_20=TARGET_POPULATION,
                pop_over_20_unvaxed=unvaxed,
                pop_over_20_dose1=cum_total_dose1 - cum_total_dose2,
                pop_over_20_dose2=cum_total_dose2,
                daily_deaths_unvaxed=daily_deaths_unvaxed,
                daily_deaths_dose1=daily_deaths_dose1,
                daily_deaths_dose2=daily_deaths_dose2,
            )
        )

    data_file = '/tmp/covid19.analysis.mortality_curve.tsv'
    tsv.write(data_file, data_list)


if __name__ == '__main__':
    analysis()
