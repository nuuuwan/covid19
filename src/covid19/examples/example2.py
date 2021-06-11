"""Example 2."""

import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

from covid19 import covid_data

timeseries = covid_data.load_jhu_data()['LK']['timeseries']

x = list(map(
    lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
    timeseries,
))
y = list(map(
    lambda d: d['new_deaths'],
    timeseries,
))

plt.bar(x, y, color='red')
ax = plt.gca()
ax.get_yaxis().set_major_formatter(
    tkr.FuncFormatter(lambda x, p: format(int(x), ','))
)
plt.gcf().autofmt_xdate()
plt.title('Daily COVID19 Deaths in Sri Lanka.')
plt.suptitle(
    'Data Source: https://github.com/CSSEGISandData/COVID-19',
    fontsize=6,
)
plt.show()
