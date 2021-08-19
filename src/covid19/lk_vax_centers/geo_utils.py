from deep_translator import GoogleTranslator
from utils import timex
from utils.cache import cache

CACHE_NAME = 'covid19.lk_vax_centers'

translator_si = GoogleTranslator(source='english', target='sinhala')


@cache('CACHE_NAME', timex.SECONDS_IN.YEAR)
def get_location_info_inner(gmaps, search_text):
    return gmaps.geocode(search_text)


def get_location_info(gmaps, district, police, center):
    if 'car park' in center.lower() or 'mobile' in center.lower():
        center = f'{police} {center}'

    search_text = f'{center}, {district} District, Sri Lanka'
    geocode_results = get_location_info_inner(gmaps, search_text)

    if (
        len(geocode_results) == 0
        or 'Sri Lanka' not in geocode_results[0]['formatted_address']
    ):
        search_text = f'{police} Police Station, Sri Lanka'
        geocode_results = get_location_info_inner(gmaps, search_text)

    if (
        len(geocode_results) == 0
        or 'Sri Lanka' not in geocode_results[0]['formatted_address']
    ):
        return None, None, None

    geocode_result = geocode_results[0]

    lat = geocode_result['geometry']['location']['lat']
    lng = geocode_result['geometry']['location']['lng']
    formatted_address = geocode_result['formatted_address']
    return lat, lng, formatted_address
