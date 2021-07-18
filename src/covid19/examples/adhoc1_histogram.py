import os

import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

from covid19 import _utils, lk_data

START_DAYS_AGO = 60
FIELD_KEY = 'new_deaths'
label = FIELD_KEY.replace('_', ' ').title()
GROUP_BY = 5
timeseries_period = lk_data.get_timeseries()[-START_DAYS_AGO:]
x = [d[FIELD_KEY] for d in timeseries_period]
print(x)
n = len(x)
unique_n = len(list(set(x)))
print(n, unique_n)

start_date = timeseries_period[0]['date'][:10]
end_date = timeseries_period[-1]['date'][:10]
print(min(x), max(x))
bins = [bin for bin in range(min(x), max(x), GROUP_BY)]
plt.hist(x, bins=bins, color=['red'])
ax = plt.gca()
ax.get_yaxis().set_major_formatter(
    tkr.FuncFormatter(lambda x, p: format(float(x), '.0f'))
)
ax.grid()

plt.suptitle(
    'COVID19 in Sri Lanka (%s to %s)' % (start_date, end_date),
    fontsize=12,
)
plt.title('%s Per Day (X) vs. Number of Days (Y) Histogram' % label)
plt.ylabel('Number of Days')
plt.xlabel('%s per Day' % label)

image_file = '/tmp/covid19.adhoc1_histogram.%s.%s.%s.group%d.png' % (
    FIELD_KEY,
    start_date,
    end_date,
    GROUP_BY,
)

fig = plt.gcf()
fig.set_size_inches(8, 4.5)
fig.savefig(image_file)

plt.close()
_utils.log.info('Saved to %s', image_file)
os.system('open %s' % image_file)
