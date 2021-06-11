"""Pull covid data from various online sources."""
import logging
import time
import datetime
import pycountry
import pypopulation
from utils import www, timex
from utils.cache import cache

CACHE_NAME = 'covid19.covid_data'
JHU_URL = 'https://pomber.github.io/covid19/timeseries.json'
OWID_VAC_URL = 'https://raw.githubusercontent.com/owid/covid-19-data' \
    + '/master/public/data/vaccinations/vaccinations.json'

COUNTRY_NAME_MAP = {
    'Burma': 'Myanmar',
    'Congo (Brazzaville)': 'Republic of the Congo',
    'Congo (Kinshasa)': 'Congo, The Democratic Republic of the',
    'Korea, South': 'Republic of Korea',
    'Laos': 'Lao People\'s Democratic Republic',
    'Taiwan*': 'Taiwan',
    'West Bank and Gaza': 'Palestine',
}


@cache(CACHE_NAME, 3600)
def load_jhu_data_raw():
    """Pull data from JHU's CSSE.

    COVID-19 Data Repository by the Center for Systems Science and Engineering
    (CSSE) at Johns Hopkins University.

    Source: https://pomber.github.io/covid19/timeseries.json via
        https://github.com/CSSEGISandData/COVID-19
    """
    return www.read_json(JHU_URL)


@cache(CACHE_NAME, 3600)
def load_owid_vaccination_data_raw():
    """Pull Our World in Data Vaccination Data.

    Source: https://github.com/owid/covid-19-data
    """
    return www.read_json(OWID_VAC_URL)


@cache(CACHE_NAME, 3600)
def load_jhu_data():  # TODO: Should change this name to reflect OWID
    """Wrap load_jhu_data_raw, to make data more useful."""

    # vaccine data (from owid)
    vac_data = load_owid_vaccination_data_raw()
    country_to_date_to_vac_data = {}
    for country_data in vac_data:
        country_alpha_3 = country_data['iso_code']

        date_to_vac_data = {}
        for date_data in country_data['data']:
            unixtime = timex.parse_time(date_data['date'], '%Y-%m-%d')
            date_to_vac_data[unixtime] = {
                'cum_vaccinations':
                    date_data.get('total_vaccinations', 0),
                'cum_people_vaccinated':
                    date_data.get('people_vaccinated', 0),
                'cum_people_fully_vaccinated':
                    date_data.get('people_fully_vaccinated', 0),
            }
        country_to_date_to_vac_data[country_alpha_3] = date_to_vac_data

    # original jhu data
    def _cleaned_timeseries_item(item, prev_item, country_alpha_3):
        unixtime = timex.parse_time(item['date'], '%Y-%m-%d')
        vaccination_data = country_to_date_to_vac_data \
            .get(country_alpha_3, {}) \
            .get(unixtime, {
                'cum_vaccinations': 0,
                'cum_people_vaccinated': 0,
                'cum_people_fully_vaccinated': 0,
            })

        for key in [
            'cum_vaccinations',
            'cum_people_vaccinated',
            'cum_people_fully_vaccinated',
        ]:
            vaccination_data[key] = max(
                vaccination_data[key],
                prev_item.get(key, 0),
            )

        return {
            'date': str(datetime.datetime.fromtimestamp(unixtime)),
            'unixtime': unixtime,
            'cum_confirmed': item['confirmed'],
            'cum_deaths': item['deaths'],
            'cum_recovered': item['recovered'],

            'active':
                item['confirmed'] - item['deaths'] - item['recovered'],

            'new_confirmed':
                item['confirmed'] - prev_item.get('cum_confirmed', 0),
            'new_deaths':
                item['deaths'] - prev_item.get('cum_deaths', 0),
            'new_recovered':
                item['recovered'] - prev_item.get('cum_recovered', 0),
        } | vaccination_data

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
            cleaned_item = \
                _cleaned_timeseries_item(item, prev_item, country.alpha_3)
            cleaned_timeseries.append(cleaned_item)
            prev_item = cleaned_item

        data[country.alpha_2] = {
            'country_name': country.name,
            'country_alpha_2': country.alpha_2,
            'country_alpha_3': country.alpha_3,
            'population': pypopulation.get_population(country.alpha_2),
            'timeseries': cleaned_timeseries,
        }

    return data
