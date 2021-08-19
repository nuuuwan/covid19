import argparse
import os

from deep_translator import GoogleTranslator
import googlemaps

from utils import timex, tsv, www
from utils.cache import cache

from covid19._utils import log
from covid19.lk_vax_centers import lk_vax_center_utils

CACHE_NAME = 'covid19.lk_vax_centers'


def get_google_drive_api_key():
    """Construct Twitter from Args."""
    parser = argparse.ArgumentParser(description='lk_vax_centers')
    parser.add_argument(
        '--google_drive_api_key',
        type=str,
        required=False,
        default=None,
    )
    args = parser.parse_args()
    return args.google_drive_api_key


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


translator_si = GoogleTranslator(source='english', target='sinhala')


@cache('CACHE_NAME', timex.SECONDS_IN.YEAR)
def translate_si(text):
    """Translate text."""
    if len(text) <= 3:
        return text
    return translator_si.translate(text)


translator_ta = GoogleTranslator(source='english', target='tamil')


@cache('CACHE_NAME', timex.SECONDS_IN.YEAR)
def translate_ta(text):
    """Translate text."""
    if len(text) <= 3:
        return text
    return translator_ta.translate(text)


@cache(CACHE_NAME, timex.SECONDS_IN.HOUR)
def get_vax_center_index():
    remote_dir = 'https://raw.githubusercontent.com/nuuuwan/covid19/data'
    ut = timex.get_unixtime()
    all_data_list = []
    while True:
        date_id = timex.get_date_id(ut)
        remote_data_url = os.path.join(
            remote_dir,
            f'covid19.lk_vax_centers.{date_id}.tsv',
        )
        if not www.exists(remote_data_url):
            break
        data_list = www.read_tsv(remote_data_url)
        n_centers = len(data_list)
        log.info(f'Read {n_centers} Vax Centers from {remote_data_url}')

        all_data_list += data_list

        ut -= timex.SECONDS_IN.DAY

    all_data_list.reverse()
    vax_center_index = dict(
        zip(
            list(
                map(
                    lambda data: lk_vax_center_utils.get_vax_center_key(
                        data['district'],
                        data['police'],
                        data['center'],
                    ),
                    all_data_list,
                )
            ),
            all_data_list,
        )
    )
    n_index = len(vax_center_index.keys())
    log.info(f'Built vax center index with {n_index} entries')
    return vax_center_index


def expand_for_data(vax_center_index, gmaps, data):
    district = data['district']
    police = data['police']
    center = data['center']
    dose1 = data['dose1']
    dose2 = data['dose2']

    vax_center_key = lk_vax_center_utils.get_vax_center_key(
        district, police, center
    )
    if vax_center_key in vax_center_index:
        data_clone = vax_center_index[vax_center_key]

        district_si = data_clone['district_si']
        police_si = data_clone['police_si']
        center_si = data_clone['center_si']

        district_ta = data_clone['district_ta']
        police_ta = data_clone['police_ta']
        center_ta = data_clone['center_ta']

        lat = data_clone['lat']
        lng = data_clone['lng']
        formatted_address = data_clone['formatted_address']

        formatted_address_si = data_clone['formatted_address_si']
        formatted_address_ta = data_clone['formatted_address_ta']

        log.info(f'Expanded: {vax_center_key} (from history)')

    else:

        district_si = translate_si(district)
        police_si = translate_si(police)
        center_si = translate_si(center)

        district_ta = translate_ta(district)
        police_ta = translate_ta(police)
        center_ta = translate_ta(center)

        lat, lng, formatted_address = get_location_info(
            gmaps,
            district,
            police,
            center,
        )

        formatted_address_si, formatted_address_ta = None, None
        if formatted_address:
            formatted_address_si = translate_si(formatted_address)
            formatted_address_ta = translate_ta(formatted_address)

        log.info(f'Expanded: {vax_center_key}')

    return dict(
        district=district,
        police=police,
        center=center,
        dose1=dose1,
        dose2=dose2,
        lat=lat,
        lng=lng,
        formatted_address=formatted_address,
        district_si=district_si,
        police_si=police_si,
        center_si=center_si,
        formatted_address_si=formatted_address_si,
        district_ta=district_ta,
        police_ta=police_ta,
        center_ta=center_ta,
        formatted_address_ta=formatted_address_ta,
    )


def expand(date_id):
    tsv_basic_file = lk_vax_center_utils.get_file(date_id, 'basic.tsv')
    if not os.path.exists(tsv_basic_file):
        log.error(f'{tsv_basic_file} does not exist. Aborting.')
        return False
    data_list = tsv.read(tsv_basic_file)

    vax_center_index = get_vax_center_index()
    google_drive_api_key = get_google_drive_api_key()
    if not google_drive_api_key:
        log.error('Missing google_drive_api_key')
        return False
    gmaps = googlemaps.Client(key=google_drive_api_key)

    expanded_data_list = list(
        map(
            lambda data: expand_for_data(vax_center_index, gmaps, data),
            data_list,
        )
    )

    tsv_file = lk_vax_center_utils.get_file(date_id, 'tsv')
    tsv.write(tsv_file, expanded_data_list)
    n_data_list = len(expanded_data_list)
    log.info(f'Wrote {n_data_list} rows to {tsv_file}')
    return expanded_data_list


if __name__ == '__main__':
    date_id = timex.get_date_id()
    expand(date_id)
