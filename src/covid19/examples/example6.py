"""Example 6."""

import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

from covid19 import covid_data

country_alpha_2 = 'MY'
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
        lambda d: (d['cum_people_vaccinated'] - d['cum_people_fully_vaccinated'])
        / population,
        timeseries,
    )
)

plt.stackplot(x, y1, y2, colors=['green', 'lightgreen'])

plt.title('%% People Vaccinated in %s.' % (country_name))
plt.suptitle(
    'Data Source: https://github.com/CSSEGISandData/COVID-19'
    + '& https://www.hpb.health.gov.lk/api/get-current-statistical',
    fontsize=6,
)
plt.legend(
    ['Fully', 'Partially'],
    loc='upper left',
)

ax = plt.gca()
ax.get_yaxis().set_major_formatter(
    tkr.FuncFormatter(lambda x, p: format(float(x), '.2%'))
)

fig = plt.gcf()
fig.autofmt_xdate()
fig.set_size_inches(12, 6.75)
fig.savefig('/tmp/example6_%s.png' % (country_alpha_2), dpi=600)

plt.show()
