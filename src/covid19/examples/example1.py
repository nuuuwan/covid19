"""Example 1."""

import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

from covid19 import covid_data

timeseries = covid_data.load_jhu_data()['IN']['timeseries']

x = list(map(
    lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
    timeseries,
))
y = list(map(
    lambda d: d['active'],
    timeseries,
))

plt.plot(x, y, color='orange')
ax = plt.gca()
ax.get_yaxis().set_major_formatter(
    tkr.FuncFormatter(lambda x, p: format(int(x), ','))
)
plt.gcf().autofmt_xdate()
plt.title('Active COVID19 Cases in India.')
plt.suptitle(
    'Data Source: https://github.com/CSSEGISandData/COVID-19',
    fontsize=6,
)
plt.show()
