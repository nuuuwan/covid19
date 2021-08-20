import os
import json
from utils import timex, tsv, geo


from gig import ents
from covid19._utils import log
from covid19.lk_vax_centers import (google_utils, lk_vax_center_utils,
                                    metadata_fix)

MAX_DIS_CENTER_TO_POLICE = 20

def round_x(x):
    return round((float)(x), 6)


def expand_for_data(gmap, data):
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

    # Add district info
    district_data = ents.get_entities_by_name_fuzzy(district, 'district')[0]
    data['district_name_norm'] = district_data['name']
    data['district_id'] = district_data['id']
    data['district_lat'] = round_x(district_data['centroid'][0])
    data['district_lng'] = round_x(district_data['centroid'][1])

    # Add police info
    police_list = ents.get_entities_by_name_fuzzy(police, 'ps')

    if police == 'Agalawatta':
        data['ps_name_norm'] = 'Agalawatta'
        data['ps_id'] = 'Unknown'
        data['ps_lat'] = round_x(6.54256638418913)
        data['ps_lng'] = round_x(80.15717812090199)
    elif len(police_list) > 0:
        police_data = police_list[0]
        data['ps_name_norm'] = police_data ['name']
        data['ps_id'] = police_data ['ps_id']
        data['ps_lat'] = round_x(police_data ['lat'])
        data['ps_lng'] = round_x(police_data ['lng'])
    else:
        data['ps_name_norm'] = 'Unknown'
        data['ps_id'] = 'Unknown'
        data['ps_lat'] = data['district_lat']
        data['ps_lng'] = data['district_lng']
        tags.append('#PoliceStationUnknown')

    # Add location info
    location_search_center = center if (alt_name == '') else alt_name
    lat, lng, formatted_address = google_utils.get_location_info(
        gmap,
        district,
        police,
        location_search_center,
    )

    if lat is None:
        data['lat'] = data['ps_lat']
        data['lng'] = data['ps_lat']
        data['formatted_address'] = ''
        tags.append('#CenterLocationUnknown')
        data['dis_center_to_police'] = 0

    else:
        data['lat'] = round_x(lat)
        data['lng'] = round_x(lng)
        data['formatted_address'] = formatted_address

        dis_center_to_police = geo.get_distance(
            [lat, lng],
            [data['ps_lat'], data['ps_lng']]
        )
        data['dis_center_to_police'] = round_x(dis_center_to_police)

        if dis_center_to_police > MAX_DIS_CENTER_TO_POLICE:
            tags.append('#LikelyIncorrectAddress')


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

    gmaps = google_utils.get_gmaps()
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
