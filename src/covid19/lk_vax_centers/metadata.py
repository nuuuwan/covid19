import argparse
import os

import googlemaps
from gig import ents
from utils import ds, timex, tsv, www

from covid19._utils import log
from covid19.lk_vax_centers import (geo_utils, lk_vax_center_utils,
                                    translate_utils)
from covid19.lk_vax_centers.lk_vax_center_constants import REMOTE_DATA_DIR


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


def backpopulate(date_id):
    ut = timex.parse_time(date_id, '%Y%m%d')
    metadata_index = {}
    while True:
        cur_date_id = timex.get_date_id(ut)
        remote_data_url = os.path.join(
            REMOTE_DATA_DIR,
            f'covid19.lk_vax_centers.{cur_date_id}.tsv',
        )
        if www.exists(remote_data_url):
            data_list = www.read_tsv(remote_data_url)
            n_centers = len(data_list)
            log.info(f'Read {n_centers} Vax Centers from {remote_data_url}')

            for data in data_list:
                if data['center'] == 'Elpitiya Base Hospital':
                    print(cur_date_id, data)
                fuzzy_key = lk_vax_center_utils.get_fuzzy_key(
                    data['district'],
                    data['police'],
                    data['center'],
                )
                if fuzzy_key in metadata_index:
                    continue
                metadata_index[fuzzy_key] = data

        else:
            if cur_date_id != date_id:
                break
        ut -= timex.SECONDS_IN.DAY

    metadata_list = []
    for fuzzy_key, data in metadata_index.items():
        meta_d = dict(
            fuzzy_key=fuzzy_key,
            district=data['district'],
            police=data['police'],
            center=data['center'],
            lat=data['lat'],
            lng=data['lng'],
            formatted_address=data['formatted_address'],
            district_si=data['district_si'],
            police_si=data['police_si'],
            center_si=data['center_si'],
            formatted_address_si=data['formatted_address_si'],
            district_ta=data['district_ta'],
            police_ta=data['police_ta'],
            center_ta=data['center_ta'],
            formatted_address_ta=data['formatted_address_ta'],
        )
        metadata_list.append(meta_d)

    metadata_list = sorted(
        metadata_list,
        key=lambda d: d['fuzzy_key'],
    )

    metadata_file = lk_vax_center_utils.get_file(date_id, 'metadata.tsv')
    tsv.write(metadata_file, metadata_list)
    n_data_list = len(metadata_list)
    log.info(f'Wrote {n_data_list} metadata rows to {metadata_file}')


def get_metadata_list(date_id):
    metadata_file = lk_vax_center_utils.get_file(date_id, 'metadata.tsv')
    return tsv.read(metadata_file)


def get_metadata_index(date_id):
    return ds.dict_list_to_index(
        get_metadata_list(date_id),
        'fuzzy_key',
    )


def populate(date_id):
    tsv_basic_file = lk_vax_center_utils.get_file(date_id, 'basic.tsv')
    if not os.path.exists(tsv_basic_file):
        log.error(f'{tsv_basic_file} does not exist. Aborting.')
        return False

    data_list = tsv.read(tsv_basic_file)

    metadata_index = get_metadata_index(date_id)
    google_drive_api_key = get_google_drive_api_key()
    if not google_drive_api_key:
        log.error('Missing google_drive_api_key')
        return False

    gmaps = googlemaps.Client(key=google_drive_api_key)

    for data in data_list:
        district = data['district']
        police = data['police']
        center = data['center']
        fuzzy_key = lk_vax_center_utils.get_fuzzy_key(district, police, center)

        if fuzzy_key not in metadata_index:
            log.info(f'Finding metadata for {district.upper()}/{police}/{center}')

            district_si = translate_utils.translate_si(district)
            police_si = translate_utils.translate_si(police)
            center_si = translate_utils.translate_si(center)

            district_ta = translate_utils.translate_ta(district)
            police_ta = translate_utils.translate_ta(police)
            center_ta = translate_utils.translate_ta(center)

            lat, lng, formatted_address = geo_utils.get_location_info(
                gmaps,
                district,
                police,
                center,
            )

            formatted_address_si, formatted_address_ta = None, None
            if formatted_address:
                formatted_address_si = translate_utils.translate_si(
                    formatted_address
                )
                formatted_address_ta = translate_utils.translate_ta(
                    formatted_address
                )

            meta_d = dict(
                fuzzy_key=fuzzy_key,
                district=district,
                police=police,
                center=center,
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
            metadata_index[fuzzy_key] = meta_d

    metadata_list = list(metadata_index.values())

    expanded_metadata_list = []
    for meta_d in metadata_list:
        # Add District ID
        district = meta_d['district']
        district_data_list = ents.get_entities_by_name_fuzzy(
            district, 'district'
        )
        if district_data_list:
            district_data = district_data_list[0]
            meta_d['district_id'] = district_data['district_id']
            meta_d['district'] = district_data['name']

        else:
            log.warn(f'Could not find district data for {district}')
            meta_d['district_id'] = None

        expanded_metadata_list.append(meta_d)

    expanded_metadata_list = sorted(
        expanded_metadata_list,
        key=lambda meta_d: meta_d['district_id'] + meta_d['fuzzy_key'],
    )

    metadata_file = lk_vax_center_utils.get_file(date_id, 'metadata.tsv')
    tsv.write(metadata_file, expanded_metadata_list)
    n_data_list = len(expanded_metadata_list)
    log.info(f'Wrote {n_data_list} metadata rows to {metadata_file}')


if __name__ == '__main__':
    date_id = timex.get_date_id()
    # backpopulate(date_id)
    populate(date_id)
