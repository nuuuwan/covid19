import argparse

import googlemaps
from utils.cache import cache

from covid19.lk_vax_centers.lk_vax_center_constants import (CACHE_DIR,
                                                            CACHE_TIMEOUT)


def get_google_api_key():
    """Construct Twitter from Args."""
    parser = argparse.ArgumentParser(description='lk_vax_centers')
    parser.add_argument(
        '--google_api_key',
        type=str,
        required=False,
        default=None,
    )
    args = parser.parse_args()
    return args.google_api_key


def get_gmaps():
    google_api_key = get_google_api_key()
    gmaps = googlemaps.Client(key=google_api_key)
    return gmaps


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
        lat = geocode_result['geometry']['location']['lat']
        lng = geocode_result['geometry']['location']['lng']
        formatted_address = geocode_result['formatted_address']
        return [lat, lng, formatted_address]

    return None


def get_location_info(gmaps, district, police, center):
    if 'car park' in center.lower():
        center = f'{police} {center}'

    if 'mobile' not in center.lower():

        if 'moh' in center.lower() or 'hospital' in center.lower():
            search_text = f'{center}'
            geocode_results = get_location_info_inner(gmaps, search_text)
            if geocode_results:
                return geocode_results

        search_text = f'{center}, {police}, {district} District, Sri Lanka'
        geocode_results = get_location_info_inner(gmaps, search_text)
        if geocode_results:
            return geocode_results

        search_text = f'{center}, {district} District, Sri Lanka'
        geocode_results = get_location_info_inner(gmaps, search_text)
        if geocode_results:
            return geocode_results

        search_text = f'{center}, Sri Lanka'
        geocode_results = get_location_info_inner(gmaps, search_text)
        if geocode_results:
            return geocode_results



    return None, None, None
