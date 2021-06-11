"""Sri Lanka specific COVID19 data."""

from utils import www
from utils.cache import cache

from covid19 import covid_data

CACHE_NAME = 'covid19.lk_data'
HPB_URL = 'https://www.hpb.health.gov.lk/api/get-current-statistical'


@cache(CACHE_NAME)
def load_hpb_data_raw():
    """Pull data from HPB.

    Health Promotion Bureau of Sri Lanka.

    Source: https://www.hpb.health.gov.lk/api/get-current-statistical
    """
    return www.read_json(HPB_URL)


def get_timeseries():
    """Extract timeseries for Sri Lanka."""
    lk_jhu_timeseries = covid_data.load_jhu_data()['LK']['timeseries']
    hpb_data = load_hpb_data_raw()
    daily_pcr_testing_data = hpb_data['data']['daily_pcr_testing_data']

    t_to_tests = dict(zip(
        list(map(
            lambda x: covid_data.parse_time(x['date']),
            daily_pcr_testing_data,
        )),
        list(map(
            lambda x: (int)(x['count']),
            daily_pcr_testing_data,
        )),
    ))

    def _add_pcr_test_data(item):
        unixtime = item['unixtime']
        item['new_pcr_tests'] = t_to_tests.get(unixtime, 0)
        return item

    lk_timeseries = list(map(
        _add_pcr_test_data,
        lk_jhu_timeseries,
    ))

    return lk_timeseries
