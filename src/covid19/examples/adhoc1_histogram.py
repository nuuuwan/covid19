import os
import logging
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

from covid19 import lk_data, _utils





DAYS_AGO = 60
FIELD_KEY = 'new_deaths'
label = FIELD_KEY.replace('_', ' ').title()
GROUP_BY = 10
timeseries_period = lk_data.get_timeseries()[-DAYS_AGO:]
x = [d[FIELD_KEY] for d in timeseries_period]

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
    'COVID19 in Sri Lanka (%d days from %s to %s)'
    % (DAYS_AGO, start_date, end_date),
    fontsize=12,
)
plt.title('%s Per Day (X) vs. Number of Days (Y) Histogram' % label)
plt.ylabel('Number of Days')
plt.xlabel('%s per Day' % label)

image_file = '/tmp/covid19.adhoc1_histogram.%s.days%d.group%d.png' % (FIELD_KEY, DAYS_AGO, GROUP_BY)

fig = plt.gcf()
fig.savefig(image_file)
plt.close()
_utils.log.info('Saved to %s', image_file)
os.system('open %s' % image_file)
