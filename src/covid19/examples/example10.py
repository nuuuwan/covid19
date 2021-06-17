"""Example 10."""

import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np

from covid19 import covid_data

country_alpha2 = 'LK'
country_data = covid_data.load_jhu_data()[country_alpha2]
days_window = 56
timeseries = country_data['timeseries']

x = list(map(
    lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
    timeseries[-days_window:],
))
y = list(map(
    lambda d: d['new_deaths'],
    timeseries[-days_window:],
))
plt.bar(x, y, color='pink')

N = 7
x2 = list(map(
    lambda d: datetime.datetime.fromtimestamp(d['unixtime'] + N * 86400),
    timeseries[(-days_window - N):],
))
y2 = list(map(
    lambda d: d['new_deaths'],
    timeseries[(-days_window - N):],
))
y2 = np.convolve(y2, np.ones(N) / N, 'valid')
plt.plot(x2[:-(N - 1)], y2, color='red')

plt.title(
    'Daily COVID19 Deaths in %s (during the last %d days) & %d-day moving average.' % (
        country_data['country_name'],
        days_window,
        N,
    ),
)
plt.suptitle(
    'Data Source: https://github.com/CSSEGISandData/COVID-19 '
    + '& https://www.hpb.health.gov.lk/api/get-current-statistical',
    fontsize=6,
)

ax = plt.gca()
ax.get_yaxis().set_major_formatter(
    tkr.FuncFormatter(lambda x, p: format(int(x), ','))
)

fig = plt.gcf()
fig.autofmt_xdate()
fig.set_size_inches(12, 6.75)
fig.savefig(
    '/tmp/example10.%s.%d.%d.png' % (country_alpha2, days_window, N),
    dpi=100,
)

plt.show()
