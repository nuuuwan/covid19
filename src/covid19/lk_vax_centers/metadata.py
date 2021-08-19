import os

from utils import ds, timex, tsv, www

from covid19._utils import log
from covid19.lk_vax_centers import lk_vax_center_utils
from covid19.lk_vax_centers.lk_vax_center_constants import REMOTE_DATA_DIR


def backpopulate(date_id):
    all_data_list = []
    ut = timex.parse_time(date_id, '%Y%m%d')
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
            all_data_list += data_list
        else:
            if cur_date_id != date_id:
                break
        ut -= timex.SECONDS_IN.DAY

    metadata_list = []
    add_set = set()
    for data in all_data_list:
        fuzzy_key = lk_vax_center_utils.get_fuzzy_key(
            data['district'],
            data['police'],
            data['center'],
        )
        if fuzzy_key in add_set:
            continue

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
        add_set.add(fuzzy_key)

    metadata_list = sorted(
        metadata_list,
        key=lambda d: d['fuzzy_key'],
    )

    metadata_file = lk_vax_center_utils.get_file(date_id, 'metadata.tsv')
    tsv.write(metadata_file, metadata_list)
    n_data_list = len(metadata_list)
    log.info(f'Wrote {n_data_list} metadata rows to {metadata_file}')


def get_metadata_index(date_id):
    metadata_file = lk_vax_center_utils.get_file(date_id, 'metadata.tsv')
    metadata_list = tsv.read(metadata_file)
    return ds.dict_list_to_index(
        metadata_list,
        'fuzzy_key',
    )



if __name__ == '__main__':
    date_id = timex.get_date_id()
    backpopulate(date_id)
    get_metadata_index(date_id)
