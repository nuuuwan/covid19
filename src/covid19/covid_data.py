"""Pull covid data from various online sources."""
import logging
import time
import datetime
import pycountry
import pypopulation
from utils import www
from utils.cache import cache

CACHE_NAME = 'covid19.covid_data.v1'
JHU_URL = 'https://pomber.github.io/covid19/timeseries.json'

COUNTRY_NAME_MAP = {
    'Burma': 'Myanmar',
    'Congo (Brazzaville)': 'Republic of the Congo',
    'Congo (Kinshasa)': 'Congo, The Democratic Republic of the',
    'Korea, South': 'Republic of Korea',
    'Laos': 'Lao People\'s Democratic Republic',
    'Taiwan*': 'Taiwan',
    'West Bank and Gaza': 'Palestine',
}


def parse_time(time_str):
    """Parse time."""
    return time.mktime(
        datetime.datetime.strptime(time_str, "%Y-%m-%d").timetuple(),
    )


@cache(CACHE_NAME)
def load_jhu_data_raw():
    """Pull data from JHU's CSSE.

    COVID-19 Data Repository by the Center for Systems Science and Engineering
    (CSSE) at Johns Hopkins University.

    Source: https://pomber.github.io/covid19/timeseries.json via
        https://github.com/CSSEGISandData/COVID-19
    """
    return www.read_json(JHU_URL)


@cache(CACHE_NAME)
def load_jhu_data():
    """Wrap load_jhu_data_raw, to make data more useful."""

    def _cleaned_timeseries_item(item, prev_item):
        unixtime = parse_time(item['date'])
        return {
            'date': str(datetime.datetime.fromtimestamp(unixtime)),
            'unixtime': unixtime,
            'cum_confirmed': item['confirmed'],
            'cum_deaths': item['deaths'],
            'cum_recovered': item['recovered'],

            'active': item['confirmed'] - item['deaths'] - item['recovered'],
            'new_confirmed': item['confirmed'] - prev_item.get('confirmed', 0),
            'new_deaths': item['deaths'] - prev_item.get('deaths', 0),
            'new_recovered': item['recovered'] - prev_item.get('recovered', 0),
        }

    raw_data = load_jhu_data_raw()
    data = {}
    for country_name, timeseries in raw_data.items():
        country_name = COUNTRY_NAME_MAP.get(country_name, country_name)
        try:
            country = pycountry.countries.search_fuzzy(country_name)[0]
        except LookupError:
            logging.error('Unknown country: %s', country_name)
            continue
        cleaned_timeseries = []
        prev_item = {}
        for item in timeseries:
            cleaned_timeseries.append(
                _cleaned_timeseries_item(item, prev_item),
            )
            prev_item = item

        data[country.alpha_2] = {
            'country_name': country.name,
            'country_alpha_2': country.alpha_2,
            'country_alpha_3': country.alpha_3,
            'population': pypopulation.get_population(country.alpha_2),
            'timeseries': cleaned_timeseries,
        }
    return data
