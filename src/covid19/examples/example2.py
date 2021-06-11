"""Example 3."""

import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

from covid19 import covid_data

country_data = covid_data.load_jhu_data()['GB']
timeseries = country_data['timeseries']

x = list(map(
    lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
    timeseries,
))
y1 = list(map(
    lambda d: d['active'],
    timeseries,
))
y2 = list(map(
    lambda d: d['cum_recovered'],
    timeseries,
))
y3 = list(map(
    lambda d: d['cum_deaths'],
    timeseries,
))

plt.stackplot(x, y1, y2, y3, colors=['blue', 'green', 'red'])

plt.title(
    'Daily COVID19 Active Cases, Total Recovered Cases, '
    + '& Total Deaths in %s.' % (country_data['country_name'])
)
plt.suptitle(
    'Data Source: https://github.com/CSSEGISandData/COVID-19 & https://www.hpb.health.gov.lk/api/get-current-statistical',
    fontsize=6,
)
plt.legend(
    ['Active', 'Total Recovered', 'Total Deaths'],
    loc='upper left',
)

ax = plt.gca()
ax.get_yaxis().set_major_formatter(
    tkr.FuncFormatter(lambda x, p: format(int(x), ','))
)

fig = plt.gcf()
fig.autofmt_xdate()
fig.set_size_inches(12, 6.75)
fig.savefig('/tmp/example2.png', dpi=600)

plt.show()
