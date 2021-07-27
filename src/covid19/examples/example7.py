"""Example 7."""

import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np

from covid19 import covid_data

country_alpha_2 = 'LK'
country_data = covid_data.load_jhu_data()[country_alpha_2]
country_name = country_data['country_name']
timeseries = country_data['timeseries']

delay = 7
mortality_rate = timeseries[-1]['cum_deaths'] / timeseries[-delay]['cum_confirmed']

x = list(
    map(
        lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
        timeseries,
    )
)
y1 = list(
    map(
        lambda d: d['new_deaths'],
        timeseries,
    )
)
N = 7
y2 = np.convolve(y1, np.ones(N) / N, 'valid')
plt.plot(x[: -(N - 1)], y2, color='red')

y3 = list(
    map(
        lambda d: d['new_confirmed'] * mortality_rate,
        [{'new_confirmed': 0} for _ in range(0, delay)] + timeseries[:-delay],
    )
)
y4 = np.convolve(y3, np.ones(N) / N, 'valid')
plt.plot(x[: -(N - 1)], y4, color='blue')

plt.title('New COVID19 Deaths in %s vs. "Predicted Deaths"' % (country_name))
plt.suptitle(
    'Data Source: https://github.com/CSSEGISandData/COVID-19 ',
    fontsize=6,
)
plt.legend(
    [
        'New Deaths (%d Data Window)' % N,
        '"Predicted Deaths" = New Confirmed Cases %d days before *  %4.2f%%'
        % (
            delay,
            mortality_rate * 100.0,
        ),
    ]
)

ax = plt.gca()
ax.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, p: format(int(x), ',')))

fig = plt.gcf()
fig.autofmt_xdate()
fig.set_size_inches(12, 6.75)
fig.savefig('/tmp/example7_%s.png' % country_alpha_2, dpi=600)

plt.show()
