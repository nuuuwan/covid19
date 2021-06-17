"""Example Tweet."""

import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np

from utils import timex

from covid19 import lk_data

ROLLING_WINDOW = 14

timeseries = lk_data.get_timeseries()
print(timeseries[-1])
latest_item = timeseries[-1]
wa_item = timeseries[-1-7]
unixtime = latest_item['unixtime']

date_id = timex.format_time(unixtime, '%Y%m%d')
date = timex.format_time(unixtime, '%Y-%m-%d')

ts_active = list(map(lambda _i: _i['active'], timeseries))

ts_new_deaths = list(map(lambda _i: _i['new_deaths'], timeseries))

ts_new_pcr_tests = list(map(lambda _i: _i['new_pcr_tests'], timeseries))

ts_cum_vaccinations = \
    list(map(lambda _i: _i['cum_vaccinations'], timeseries))
ts_cum_people_vaccinated = \
    list(map(lambda _i: _i['cum_people_vaccinated'], timeseries))
ts_cum_people_fully_vaccinated = \
    list(map(lambda _i: _i['cum_people_fully_vaccinated'], timeseries))

active = ts_active[-1]
active_wa = ts_active[-8]
delta_active = active - active_wa
active_arrow = '🔴' if (delta_active > 0) else '🟢'

new_deaths_rwday = sum(ts_new_deaths[-ROLLING_WINDOW:]) / ROLLING_WINDOW
new_deaths_rwday_wa = \
    sum(ts_new_deaths[-ROLLING_WINDOW-7:-7]) / ROLLING_WINDOW
delta_new_deaths = new_deaths_rwday - new_deaths_rwday_wa
new_deaths_rwday_arrow = '🔴' if (delta_new_deaths > 0) else '🟢'

new_vacci_rwday = (ts_cum_vaccinations[-1] - ts_cum_vaccinations[-ROLLING_WINDOW-1]) / ROLLING_WINDOW
new_vacci_rwday_wa = (ts_cum_vaccinations[-1-7] - ts_cum_vaccinations[-ROLLING_WINDOW-1-7]) / ROLLING_WINDOW
delta_new_vacci = new_vacci_rwday - new_vacci_rwday_wa
new_vacci_rwday_arrow = '🟢' if (delta_new_vacci > 0) else '🔴'

POPULATION = 21_800_000
vacci_dose_1 = ts_cum_people_vaccinated[-1]
vacci_dose_2 = ts_cum_people_fully_vaccinated[-1]
p_vacci_dose_1 = vacci_dose_1 / POPULATION
p_vacci_dose_2 = vacci_dose_2 / POPULATION

new_pcr_tests_rwday = sum(ts_new_pcr_tests[-ROLLING_WINDOW:]) / ROLLING_WINDOW
new_pcr_tests_rwday_wa = sum(ts_new_pcr_tests[-ROLLING_WINDOW-7:-7]) / ROLLING_WINDOW
delta_new_pcr_tests = new_pcr_tests_rwday - new_pcr_tests_rwday_wa
new_pcr_tests_rwday_arrow = '🟢' if (delta_new_pcr_tests > 0) else '🔴'


tweet_text = '''{date} #COVID19SL

{active_arrow} Active: {active:,} ({delta_active:+,} week ago)

{new_deaths_rwday_arrow} Dly Deaths﹘{ROLLING_WINDOW}day avg: {new_deaths_rwday:,.0f} ({delta_new_deaths:+,.0f})

{new_pcr_tests_rwday_arrow} Dly PCR Tests﹘{ROLLING_WINDOW}day avg: {new_pcr_tests_rwday:,.0f} ({delta_new_pcr_tests:+,.0f})

{new_vacci_rwday_arrow} Dly Vaxs﹘{ROLLING_WINDOW}day avg: {new_vacci_rwday:,.0f} ({delta_new_vacci:+,.0f})
- Pop vaxed: {p_vacci_dose_1:.1%}
- Pop fully vaxed: {p_vacci_dose_2:.1%}

@HPBSriLanka @JHUSystems @OurWorldInData
#lka #SriLanka
'''.format(
    ROLLING_WINDOW=ROLLING_WINDOW,
    active=active,
    active_arrow=active_arrow,
    new_vacci_rwday=new_vacci_rwday,
    date=date,
    delta_new_vacci=delta_new_vacci,
    delta_active=delta_active,
    delta_new_deaths=delta_new_deaths,
    new_deaths_rwday=new_deaths_rwday,
    new_deaths_rwday_arrow=new_deaths_rwday_arrow,
    new_vacci_rwday_arrow=new_vacci_rwday_arrow,
    p_vacci_dose_1=p_vacci_dose_1,
    p_vacci_dose_2=p_vacci_dose_2,
    new_pcr_tests_rwday_arrow=new_pcr_tests_rwday_arrow,
    new_pcr_tests_rwday=new_pcr_tests_rwday,
    delta_new_pcr_tests=delta_new_pcr_tests,
)
print(tweet_text)
print(len(tweet_text))
