"""Example 2."""

import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np

from covid19 import lk_data

timeseries = lk_data.get_timeseries()

x = list(map(
    lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
    timeseries,
))

y = list(map(
    lambda d: d['new_confirmed'] / d['new_pcr_tests'] \
        if d['new_pcr_tests'] > 10 \
        else 0,
    timeseries,
))
plt.plot(x, y, color='pink')
N = 14
y = np.convolve(y, np.ones(N) / N, 'valid')
plt.plot(x[:-(N - 1)], y, color='red')

plt.title('Daily New COVID19 Cases per PCR Tests in Sri Lanka.')
plt.suptitle(
    'Data Source: https://github.com/CSSEGISandData/COVID-19 & https://www.hpb.health.gov.lk/api/get-current-statistical',
    fontsize=6,
)
plt.legend(['Tests', '%d-Day Moving Window' % N])

ax = plt.gca()
ax.get_yaxis().set_major_formatter(
    tkr.FuncFormatter(lambda x, p: format(int(x), ','))
)

fig = plt.gcf()
fig.autofmt_xdate()
fig.set_size_inches(12, 6.75)
fig.savefig('/tmp/%s.png' % __name__, dpi=100)

plt.show()
