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
    return covid_data.load_jhu_data()['LK']['timeseries']
