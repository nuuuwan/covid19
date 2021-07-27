"""Example 3."""

import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

from covid19 import lk_data

timeseries = lk_data.get_timeseries()

x = list(
    map(
        lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
        timeseries,
    )
)
y = list(
    map(
        lambda d: d['new_confirmed'],
        timeseries,
    )
)
plt.plot(x, y, color='red')

y2 = list(
    map(
        lambda d: d['new_pcr_tests'],
        timeseries,
    )
)
plt.plot(x, y2, color='blue')

plt.title('Daily New COVID19 Cases and PCR Tests in Sri Lanka.')
plt.suptitle(
    'Data Source: https://github.com/CSSEGISandData/COVID-19',
    fontsize=6,
)
plt.legend(['Daily New Cases', 'Daily PCR Tests'])

ax = plt.gca()
ax.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x), ',')))

fig = plt.gcf()
fig.autofmt_xdate()
fig.set_size_inches(12, 6.75)
fig.savefig('/tmp/example3.png', dpi=600)

plt.show()
