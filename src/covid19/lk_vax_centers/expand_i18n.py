import os

from utils import timex, tsv

from covid19._utils import log
from covid19.lk_vax_centers import lk_vax_center_utils, metadata

CACHE_NAME = 'covid19.lk_vax_centers'


def expand_for_data(metadata_index, data):
    district = data['district']
    police = data['police']
    center = data['center']
    dose1 = data['dose1']
    dose2 = data['dose2']

    fuzzy_key = lk_vax_center_utils.get_fuzzy_key(district, police, center)
    metadata = metadata_index[fuzzy_key]
    return {**dict(fuzzy_key=fuzzy_key, dose1=dose1, dose2=dose2), **metadata}


def expand(date_id):
    tsv_basic_file = lk_vax_center_utils.get_file(date_id, 'basic.tsv')
    if not os.path.exists(tsv_basic_file):
        log.error(f'{tsv_basic_file} does not exist. Aborting.')
        return False
    data_list = tsv.read(tsv_basic_file)

    metadata_index = metadata.get_metadata_index(date_id)
    expanded_data_list = list(
        map(
            lambda data: expand_for_data(metadata_index, data),
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
