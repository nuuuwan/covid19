import os

from utils import timex, tsv

from covid19._utils import log
from covid19.lk_vax_centers import (geo_utils, lk_vax_center_utils, metadata,
                                    metadata_fix)

CACHE_NAME = 'covid19.lk_vax_centers'


def expand_for_data(gmap, data):
    district = data['district']
    police = data['police']
    center = data['center']
    fuzzy_key = lk_vax_center_utils.get_fuzzy_key(district, police, center)
    log.info(f'Expanding {fuzzy_key}')

    data['fuzzy_key'] = fuzzy_key
    alt_name = metadata_fix.FUZZY_KEY_TO_ALT_NAME.get(fuzzy_key, '')
    data['alt_name'] = alt_name

    lat, lng, formatted_address, location_type = geo_utils.get_location_info(
        gmap,
        district,
        police,
        center,
    )

    data['lat'] = lat
    data['lng'] = lng
    data['formatted_address'] = formatted_address
    data['location_type'] = location_type

    log.info(data)
    return data


def expand(date_id):
    log.info(f'Running expand for {date_id}...')
    tsv_basic_file = lk_vax_center_utils.get_file(date_id, 'basic.tsv')
    if not os.path.exists(tsv_basic_file):
        log.error(f'{tsv_basic_file} does not exist. Aborting.')
        return False
    data_list = tsv.read(tsv_basic_file)[:10]

    gmaps = metadata.get_gmaps()
    expanded_data_list = list(
        map(
            lambda data: expand_for_data(gmaps, data),
            data_list,
        )
    )

    tsv_file = lk_vax_center_utils.get_file(date_id, 'noi18n.tsv')
    tsv.write(tsv_file, expanded_data_list)
    n_data_list = len(expanded_data_list)
    log.info(f'Wrote {n_data_list} rows to {tsv_file}')
    return expanded_data_list


if __name__ == '__main__':
    date_id = timex.get_date_id()
    expand(date_id)
