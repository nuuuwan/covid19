import re

from utils import timex


def get_file(date_id, ext):
    return f'/tmp/covid19.lk_vax_centers.{date_id}.{ext}'


def get_fuzzy_key(district, police, center):
    s = f'{district}{police}{center}'
    s = s.upper()
    s = re.sub(r'[^A-Z]', '', s)
    s = re.sub(r'[AEIOU]', '', s)
    return s


def get_fuzzy_fuzzy_key(police, center):
    return get_fuzzy_key('', police, center)


def get_prev_date_id(date_id):
    DATE_ID_FORMAT = '%Y%m%d'
    ut = timex.parse_time(date_id, DATE_ID_FORMAT)
    return timex.format_time(ut - timex.SECONDS_IN.DAY, DATE_ID_FORMAT)


def get_gmaps_link(lat, lng):
    return f'https://www.google.lk/maps/place/{lat}N,{lng}E'
