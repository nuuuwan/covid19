"""Example 1. Cumulative COVID19 Deaths in Sri Lanka."""

import datetime
import matplotlib.pyplot as plt

from covid19 import covid_data

lk_timeseries = covid_data.load_jhu_data()['LK']['timeseries']

x = list(map(
    lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
    lk_timeseries,
))
y = list(map(
    lambda d: d['cum_deaths'],
    lk_timeseries,
))

plt.plot(x, y)
plt.gcf().autofmt_xdate()
plt.show()
