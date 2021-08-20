import json
import os

from utils import timex, tsv

from covid19._utils import log
from covid19.lk_vax_centers import lk_vax_center_utils, translate_utils


def expand_i18n_for_data(data):
    fuzzy_key = data['fuzzy_key']
    log.info(f'Expanding i18n {fuzzy_key}')
    district = data['district']
    police = data['police']
    center = data['center']
    alt_name = data['alt_name']
    center_search = center if alt_name == '' else alt_name

    data['district_si'] = translate_utils.translate_si(district)
    data['police_si'] = translate_utils.translate_si(police)
    data['center_si'] = translate_utils.translate_si(center_search)

    data['district_ta'] = translate_utils.translate_ta(district)
    data['police_ta'] = translate_utils.translate_ta(police)
    data['center_ta'] = translate_utils.translate_ta(center_search)

    formatted_address_si, formatted_address_ta = None, None
    formatted_address = data['formatted_address']
    if formatted_address:
        formatted_address_si = translate_utils.translate_si(formatted_address)
        formatted_address_ta = translate_utils.translate_ta(formatted_address)

    data['formatted_address_si'] = formatted_address_si
    data['formatted_address_ta'] = formatted_address_ta

    print(json.dumps(data, indent=2))

    return data


def expand_i18n(date_id):
    log.info(f'Running expand for {date_id}...')
    tsv_basic_file = lk_vax_center_utils.get_file(date_id, 'noi18n.tsv')
    if not os.path.exists(tsv_basic_file):
        log.error(f'{tsv_basic_file} does not exist. Aborting.')
        return False
    data_list = tsv.read(tsv_basic_file)

    expanded_data_list = list(
        map(
            lambda data: expand_i18n_for_data(data),
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
    expand_i18n(date_id)
