"""Example 3."""

import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

from covid19 import covid_data

country_data = covid_data.load_jhu_data()['IL']
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
ax = plt.gca()
ax.get_yaxis().set_major_formatter(
    tkr.FuncFormatter(lambda x, p: format(int(x), ','))
)
plt.gcf().autofmt_xdate()
plt.title(
    'Daily COVID19 Active Cases, Total Recovered Cases, '
    + '& Total Deaths in %s.' % (country_data['country_name'])
)
plt.suptitle(
    'Data Source: https://github.com/CSSEGISandData/COVID-19',
    fontsize=6,
)
plt.legend(
    ['Active', 'Total Recovered', 'Total Deaths'],
    loc='upper left',
)
plt.show()
