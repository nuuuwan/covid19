import statistics

from utils import tsv

from covid19._utils import log
from covid19.lk_vax_centers import lk_vax_center_utils, metadata


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
        n_d_metadata_list = len(d_metadata_list)
        print(f'{district} ({n_d_metadata_list} Centers)')
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

            for meta_d in d_metadata_list:
                lat = (float)(meta_d['lat'])
                lng = (float)(meta_d['lng'])
                z_lat = (lat - mean_lat) / stdev_lat
                z_lng = (lng - mean_lng) / stdev_lng
                if abs(z_lat) > 3 or abs(z_lng) > 3:
                    center = meta_d['center']
                    police = meta_d['police']
                    district = meta_d['district']

                    print(f'\t{z_lat}\t{z_lng}\t{center}\t{police}')
                    inaccurate_centers_list.append(
                        dict(
                            district=district,
                            police=police,
                            center=center,
                        )
                    )
    inaccurate_centers_file = lk_vax_center_utils.get_file(
        date_id, 'inaccurate_centers.tsv'
    )
    tsv.write(inaccurate_centers_file, inaccurate_centers_list)
    n_inaccurate_centers = len(inaccurate_centers_list)
    log.info(f'Wrote {n_inaccurate_centers} to {inaccurate_centers_file}')


if __name__ == '__main__':
    date_id = '20210820'
    metadata.backpopulate(date_id)
    # metadata_validate(date_id)
