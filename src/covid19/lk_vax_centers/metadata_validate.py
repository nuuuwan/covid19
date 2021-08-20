import json
import os
import statistics

from utils import tsv

from covid19._utils import log
from covid19.lk_vax_centers import lk_vax_center_utils, metadata, metadata_fix


def metadata_validate(date_id):
    metadata_list = metadata.get_metadata_list(date_id)

    # validate district clusters
    district_to_metadata_list = {}
    for meta_d in metadata_list:
        district = meta_d['district']
        if district not in district_to_metadata_list:
            district_to_metadata_list[district] = []
        district_to_metadata_list[district].append(meta_d)

    inaccurate_centers_list = []
    for district, d_metadata_list in sorted(
        district_to_metadata_list.items(),
        key=lambda x: x[0],
    ):
        len(d_metadata_list)
        lat_list = list(
            map(
                lambda meta_d: (float)(meta_d['lat']),
                d_metadata_list,
            )
        )
        lng_list = list(
            map(
                lambda meta_d: (float)(meta_d['lng']),
                d_metadata_list,
            )
        )

        n = len(lat_list)
        if n > 1:
            mean_lat = statistics.mean(lat_list)
            stdev_lat = statistics.stdev(lat_list)
            mean_lng = statistics.mean(lng_list)
            stdev_lng = statistics.stdev(lng_list)

            MAX_ABS_STDEV = 2
            for meta_d in d_metadata_list:
                lat = (float)(meta_d['lat'])
                lng = (float)(meta_d['lng'])
                z_lat = (lat - mean_lat) / stdev_lat
                z_lng = (lng - mean_lng) / stdev_lng
                if abs(z_lat) > MAX_ABS_STDEV or abs(z_lng) > MAX_ABS_STDEV:
                    center = meta_d['center']
                    police = meta_d['police']
                    district = meta_d['district']
                    fuzzy_key = meta_d['fuzzy_key']

                    gmaps_link = lk_vax_center_utils.get_gmaps_link(lat, lng)
                    inaccurate_centers_list.append(
                        dict(
                            fuzzy_key=fuzzy_key,
                            district=district,
                            police=police,
                            center=center,
                            lat=lat,
                            lng=lng,
                            gmaps_link=gmaps_link,
                        )
                    )
    inaccurate_centers_file = lk_vax_center_utils.get_file(
        date_id, 'inaccurate_centers.tsv'
    )
    tsv.write(inaccurate_centers_file, inaccurate_centers_list)
    n_inaccurate_centers = len(inaccurate_centers_list)
    log.info(f'Wrote {n_inaccurate_centers} to {inaccurate_centers_file}')

    max_centers_to_validate = 5
    n_centers_validated = 0
    for inaccurate_center in inaccurate_centers_list:
        fuzzy_key = inaccurate_center['fuzzy_key']
        if fuzzy_key in metadata_fix.CORRECT_FUZZY_KEYS:
            continue
        if fuzzy_key in metadata_fix.INCORRECT_FUZZY_KEYS:
            continue
        if fuzzy_key in metadata_fix.FUZZY_KEY_TO_ALT_NAME:
            continue

        n_centers_validated += 1
        if n_centers_validated > max_centers_to_validate:
            break

        print(json.dumps(inaccurate_center, indent=2))

        center = (
            inaccurate_center['center'] + ' ' + inaccurate_center['police']
        )
        center_str = center.replace('–', ' ').replace(' ', '+')
        google_search_link = f'https://www.google.com/search?q={center_str}'
        print(google_search_link)
        os.system(f'open -a firefox "{google_search_link}"')

        gmaps_link = inaccurate_center['gmaps_link']
        os.system(f'open -a firefox "{gmaps_link}"')


if __name__ == '__main__':
    date_id = '20210820'
    metadata_validate(date_id)
