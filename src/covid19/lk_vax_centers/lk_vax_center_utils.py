def get_file(date_id, ext):
    return f'/tmp/covid19.lk_vax_centers.{date_id}.{ext}'


def get_vax_center_key(district, police, center):
    return f'{district.upper()}/{police}/{center}'
