import json
import os

from gig import ents
from utils import geo, timex, tsv

from covid19._utils import log
from covid19.lk_vax_centers import (google_utils, lk_vax_center_utils,
                                    metadata_fix)
from covid19.lk_vax_centers.lk_vax_center_utils import round_x

MAX_DIS_CENTER_TO_POLICE = 20


def build_police_index(data_list):
    police_list = list(
        map(
            lambda data: data['police'],
            data_list,
        )
    )
    police_list = list(set(police_list))

    police_index = {}
    for police in police_list:

        if police in metadata_fix.POLICE_INDEX:
            police_data = metadata_fix.POLICE_INDEX[police]

        else:
            police_ents = ents.get_entities_by_name_fuzzy(police, 'ps')
            if len(police_ents) > 0:
                police_ent = police_ents[0]
                police_data = dict(
                    ps_name_norm=police_ent['name'],
                    ps_id=police_ent['ps_id'],
                    ps_lat=round_x(police_ent['lat']),
                    ps_lng=round_x(police_ent['lng']),
                )
            else:
                log.warning(f'Unknown Police Station: {police}')
                police_data = dict(
                    ps_name_norm=None,
                    ps_id=None,
                    ps_lat=None,
                    ps_lng=None,
                )
        police_index[police] = police_data
    log.info(f'Built police_index with {len(police_list)} entries')
    return police_index


def build_district_index(data_list):
    district_list = list(
        map(
            lambda data: data['district'],
            data_list,
        )
    )
    district_list = list(set(district_list))
    district_index = {}
    for district in district_list:
        district_ents = ents.get_entities_by_name_fuzzy(district, 'district')
        if len(district_ents) > 0:
            district_ent = district_ents[0]
            district_index[district] = dict(
                district_name_norm=district_ent['name'],
                district_id=district_ent['id'],
                district_lat=round_x(district_ent['centroid'][0]),
                district_lng=round_x(district_ent['centroid'][1]),
            )
        else:
            log.warning(f'Unknown District: {district}')
            district_index[district] = dict(
                district_name_norm=None,
                district_id=None,
                district_lat=None,
                district_lng=None,
            )

    log.info(f'Built district_index with {len(district_list)} entries')
    return district_index


def expand_for_data(gmap, district_index, police_index, data):
    tags = []
    district = data['district']
    police = data['police']
    center = data['center']
    fuzzy_key = lk_vax_center_utils.get_fuzzy_key(district, police, center)
    log.info(f'Expanding {district.upper()}/{police}/{center}')

    data['fuzzy_key'] = fuzzy_key

    # Add alt_name
    alt_name = metadata_fix.FUZZY_KEY_TO_ALT_NAME.get(fuzzy_key, '')
    data['alt_name'] = alt_name

    data = {**data, **district_index[district]}
    data = {**data, **police_index[police]}

    # Add location info
    location_search_center = center if (alt_name == '') else alt_name
    lat, lng, formatted_address = google_utils.get_location_info(
        gmap,
        district,
        police,
        location_search_center,
    )

    if lat is None:
        data['lat'] = None
        data['lng'] = None
        data['formatted_address'] = None
        tags.append('#CenterLocationUnknown')
        data['dis_center_to_police'] = None

    else:
        if data['ps_lat']:
            data['lat'] = round_x(lat)
            data['lng'] = round_x(lng)
            data['formatted_address'] = formatted_address

            dis_center_to_police = geo.get_distance(
                [lat, lng], [data['ps_lat'], data['ps_lng']]
            )
            data['dis_center_to_police'] = round_x(dis_center_to_police)

            if dis_center_to_police > MAX_DIS_CENTER_TO_POLICE:
                tags.append('#CenterFarFromPolice')
        else:
            tags.append('#PoliceLocationUnknown')

    data['tags'] = '; '.join(tags)

    if tags:
        print(json.dumps(data, indent=2))
    return data


def expand(date_id):
    log.info(f'Running expand for {date_id}...')
    tsv_basic_file = lk_vax_center_utils.get_file(date_id, 'basic.tsv')
    if not os.path.exists(tsv_basic_file):
        log.error(f'{tsv_basic_file} does not exist. Aborting.')
        return False
    data_list = tsv.read(tsv_basic_file)

    district_index = build_district_index(data_list)
    police_index = build_police_index(data_list)

    gmaps = google_utils.get_gmaps()
    expanded_data_list = list(
        map(
            lambda data: expand_for_data(
                gmaps, district_index, police_index, data
            ),
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
