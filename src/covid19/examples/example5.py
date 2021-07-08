"""Example 5."""

import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

from covid19 import covid_data

jhu_data = covid_data.load_jhu_data()
country_meta_datas = [
    {'alpha_2': 'LK', 'color': 'red'},
    {'alpha_2': 'IN', 'color': 'orange'},
    {'alpha_2': 'PK', 'color': 'lightgreen'},
    {'alpha_2': 'BD', 'color': 'darkgreen'},
    {'alpha_2': 'NP', 'color': 'blue'},
    # {'alpha_2': 'AF', 'color': 'lightblue'},
    # {'alpha_2': 'MV', 'color': 'red'},
    # {'alpha_2': 'BT', 'color': 'purple'},
]

legend_labels = []
for country_meta_data in country_meta_datas:
    country_data = jhu_data[country_meta_data['alpha_2']]
    legend_labels.append(country_data['country_name'])
    timeseries = country_data['timeseries']
    population = country_data['population']

    x = list(
        map(
            lambda d: datetime.datetime.fromtimestamp(d['unixtime']),
            timeseries,
        )
    )
    y = list(
        map(
            lambda d: d['cum_people_vaccinated'] / population,
            timeseries,
        )
    )
    plt.plot(x, y, color=country_meta_data['color'])

plt.title('% People vaccinated in South Asia.')
plt.suptitle(
    'Data Source: https://github.com/CSSEGISandData/COVID-19 '
    + '& https://github.com/owid/covid-19-data',
    fontsize=6,
)
plt.legend(
    legend_labels,
    loc='upper left',
)

ax = plt.gca()
ax.get_yaxis().set_major_formatter(
    tkr.FuncFormatter(lambda x, p: format(float(x), '.2%'))
)

fig = plt.gcf()
fig.autofmt_xdate()
fig.set_size_inches(8, 4.5)
fig.savefig('/tmp/example5.png', dpi=600)

plt.show()
