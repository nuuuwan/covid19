from deep_translator import GoogleTranslator
from utils import timex
from utils.cache import cache
from covid19.lk_vax_centers.lk_vax_center_constants import CACHE_DIR, CACHE_NAME, CACHE_TIMEOUT

translator_si = GoogleTranslator(source='english', target='sinhala')


def is_valid_geocode_results(geocode_results):
    return (
        len(geocode_results) > 0 and len(geocode_results) < 3
    ) and 'Sri Lanka' in geocode_results[0]['formatted_address']


def get_location_info_inner(gmaps, search_text):
    @cache('CACHE_NAME', CACHE_TIMEOUT, CACHE_DIR)
    def get_location_info_inner_inner(search_text=search_text):
        return gmaps.geocode(search_text)

    geocode_results = get_location_info_inner_inner(search_text)
    if is_valid_geocode_results(geocode_results):
        geocode_result = geocode_results[0]
        print(geocode_result)
        lat = geocode_result['geometry']['location']['lat']
        lng = geocode_result['geometry']['location']['lng']
        formatted_address = geocode_result['formatted_address']
        return [lat, lng, formatted_address]

    return None


def get_location_info(gmaps, district, police, center):
    if 'car park' in center.lower():
        center = f'{police} {center}'

    if 'mobile' not in center.lower():
        search_text = f'{center}'
        geocode_results = get_location_info_inner(gmaps, search_text)
        if geocode_results:
            return geocode_results + ['center']

        search_text = f'{center}, Sri Lanka'
        geocode_results = get_location_info_inner(gmaps, search_text)
        if geocode_results:
            return geocode_results + ['center']

        search_text = f'{center}, {district} District, Sri Lanka'
        geocode_results = get_location_info_inner(gmaps, search_text)
        if geocode_results:
            return geocode_results + ['center']

    search_text = f'{police} Police Station, {district} District, Sri Lanka'
    geocode_results = get_location_info_inner(gmaps, search_text)
    if geocode_results:
        return geocode_results + ['police']

    search_text = f'{district} District, Sri Lanka'
    geocode_results = get_location_info_inner(gmaps, search_text)
    if geocode_results:
        return geocode_results + ['district']

    return None, None, None, 'unknown'
