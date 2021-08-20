import re


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
