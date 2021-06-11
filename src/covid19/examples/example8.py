"""Example 6."""

import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

from covid19 import covid_data

country_alpha_2 = 'IN'
country_data = covid_data.load_jhu_data()[country_alpha_2]
country_name = country_data['country_name']
timeseries = country_data['timeseries'][-150:]
population = country_data['population']

x = list(map(
    lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
    timeseries,
))
y1a = list(map(
    lambda d: d['cum_people_vaccinated'] / population,
    timeseries,
))
y1 = list(map(
    lambda d: d['cum_people_fully_vaccinated'] / population,
    timeseries,
))

days_to_second_dose1 = 7 * 10
y2 = [0 for _ in range(0, days_to_second_dose1)] + list(map(
    lambda d: d['cum_people_vaccinated'] / population,
    timeseries[:-days_to_second_dose1],
))
days_to_second_dose2 = 7 * 8
y3 = [0 for _ in range(0, days_to_second_dose2)] + list(map(
    lambda d: d['cum_people_vaccinated'] / population,
    timeseries[:-days_to_second_dose2],
))
days_to_second_dose3 = 7 * 6
y4 = [0 for _ in range(0, days_to_second_dose3)] + list(map(
    lambda d: d['cum_people_vaccinated'] / population,
    timeseries[:-days_to_second_dose3],
))

plt.plot(x, y1,  color="green")
plt.plot(x, y1a,  color="lightgreen")
plt.plot(x, y2,  color="blue")
plt.plot(x, y3,  color="purple")
plt.plot(x, y4,  color="red")

plt.title(
    '%% People Vaccinated in %s.' % (country_name)
)
plt.suptitle(
    'Data Source: https://github.com/CSSEGISandData/COVID-19'
    + '& https://www.hpb.health.gov.lk/api/get-current-statistical',
    fontsize=6,
)
plt.legend(
    [
        'Fully Vaccinated',
        'At least 1st dose',
        '%d Weeks after 1st dose' % (days_to_second_dose1 / 7),
        '%d Weeks after 1st dose' % (days_to_second_dose2 / 7),
        '%d Weeks after 1st dose' % (days_to_second_dose3 / 7)
    ],
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
