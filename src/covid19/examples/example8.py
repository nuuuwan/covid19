"""Example 6."""

import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

from covid19 import covid_data

country_alpha_2 = 'US'
country_data = covid_data.load_jhu_data()[country_alpha_2]
country_name = country_data['country_name']
timeseries = country_data['timeseries'][-150:]
population = country_data['population']

x = list(
    map(
        lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
        timeseries,
    )
)
y1 = list(
    map(
        lambda d: d['cum_people_fully_vaccinated'] / population,
        timeseries,
    )
)
y2 = list(
    map(
        lambda d: d['cum_people_vaccinated'] / population,
        timeseries,
    )
)

legend = [
    'Fully Vaccinated',
    'At least 1st dose',
]
plt.plot(x, y1, color="green")
plt.plot(x, y2, color="lightgreen")

windows = [4, 6, 8, 10, 12, 14]
n_windows = len(windows)
for i, weeks in enumerate(windows):
    days_to_second_dose1 = 7 * weeks
    y = [0 for _ in range(0, days_to_second_dose1)] + list(
        map(
            lambda d: d['cum_people_vaccinated'] / population,
            timeseries[:-days_to_second_dose1],
        )
    )
    r = 1
    g = 0.8 - 0.8 * i / n_windows
    b = g
    plt.plot(x, y, color=(r, g, b))
    legend.append('%d weeks since 1st dose' % weeks)

plt.title('%% People Vaccinated in %s.' % (country_name))
plt.suptitle(
    'Data Source: https://github.com/CSSEGISandData/COVID-19'
    + '& https://www.hpb.health.gov.lk/api/get-current-statistical',
    fontsize=6,
)
plt.legend(
    legend,
    loc='upper left',
)

ax = plt.gca()
ax.get_yaxis().set_major_formatter(
    tkr.FuncFormatter(lambda x, p: format(float(x), '.2%'))
)

fig = plt.gcf()
fig.autofmt_xdate()
fig.set_size_inches(12, 6.75)
fig.savefig('/tmp/example8_%s.png' % (country_alpha_2), dpi=300)

plt.show()
