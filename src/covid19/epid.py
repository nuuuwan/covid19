"""EPID utils."""
import json
import logging
import os
import re

from bs4 import BeautifulSoup
from utils import ds, dt, jsonx, timex, tsv, www
from utils.cache import cache

from covid19 import _utils

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('covid19.epid')

URL_EPID = 'https://www.epid.gov.lk'
URL_VAX_SUMMARY_LIST = os.path.join(
    URL_EPID,
    'web/index.php?',
    'option=com_content&view=article&id=231&lang=en',
)
REGEX_DATE_ID = r'(?P<y_str>\d{4})-(?P<m_str>\d{2})_(?P<d_str>\d{2})'
LIMITED_TEST_MODE = False


def _parse_int(x):
    if isinstance(x, float):
        return 0
    if x == '-':
        return 0
    return dt.parse_int(x.replace(',', ''), 0)


def _parse_data_format(date_id, tables):
    rows = tables[-1]
    if date_id > '20210505':
        row_3 = _utils._row_to_ints(rows[-3])
        if len(row_3) == 0:
            row_3 = _utils._row_to_ints(rows[-4])

        if len(row_3) == 6:
            row_pfizer = (
                _utils._row_to_ints(rows[-4])
                + _utils._row_to_ints(rows[-5])
                + _utils._row_to_ints(rows[-2])
            )
            row_moderna = []
        elif len(row_3) == 7:
            row_pfizer = [row_3[-1]]
            row_3 = row_3[:-1]
            row_moderna = []
        elif len(row_3) == 8:
            row_pfizer = [row_3[-2]]
            row_moderna = [row_3[-1]]
            row_3 = row_3[:-2]
        else:
            row_3 = _utils._row_to_ints(rows[-2])
            row_pfizer = []
            row_moderna = []
        pfizer_dose1 = row_pfizer[0] if row_pfizer else 0
        moderna_dose1 = row_moderna[0] if row_moderna else 0

        (
            covishield_dose1,
            covishield_dose2,
            sinopharm_dose1,
            sinopharm_dose2,
            sputnik_dose1,
            sputnik_dose2,
        ) = row_3

        if sinopharm_dose2 == 2435:
            sinopharm_dose2 = 0
    elif date_id > '20210129':
        covishields = []
        sinopharms = []
        for row in rows:
            valid_cells = list(
                filter(
                    lambda cell: '2021' not in cell,
                    row,
                )
            )
            row_new = (' '.join(valid_cells)).split(' ')

            if len(row_new) >= 2:
                covishields.append(dt.parse_int(row_new[1]))
            if len(row_new) >= 4:
                sinopharms.append(dt.parse_int(row_new[3]))
        covishield_dose1 = max(covishields)
        covishield_dose2 = covishields[-1]
        if covishield_dose2 >= covishield_dose1:
            covishield_dose2 = 0
        sinopharm_dose1 = max(sinopharms) if sinopharms else 0
        if sinopharm_dose1 == 246:
            sinopharm_dose1 = 2469

        sinopharm_dose2 = 0
        sputnik_dose1 = 0
        sputnik_dose2 = 0
        pfizer_dose1 = 0
        moderna_dose1 = 0
    else:
        covishield_dose1 = 5286
        covishield_dose2 = 0
        sinopharm_dose1 = 0
        sinopharm_dose2 = 0
        sputnik_dose1 = 0
        sputnik_dose2 = 0
        pfizer_dose1 = 0
        moderna_dose1 = 0

    total_dose1 = sum(
        [
            covishield_dose1,
            sinopharm_dose1,
            sputnik_dose1,
            pfizer_dose1,
            moderna_dose1,
        ]
    )
    total_dose2 = sum(
        [
            covishield_dose2,
            sinopharm_dose2,
            sputnik_dose2,
        ]
    )
    total = sum(
        [
            total_dose1,
            total_dose2,
        ]
    )

    parsed_data = {
        'covishield_dose1': covishield_dose1,
        'covishield_dose2': covishield_dose2,
        'sinopharm_dose1': sinopharm_dose1,
        'sinopharm_dose2': sinopharm_dose2,
        'sputnik_dose1': sputnik_dose1,
        'sputnik_dose2': sputnik_dose2,
        'pfizer_dose1': pfizer_dose1,
        'moderna_dose1': moderna_dose1,
        'total_dose1': total_dose1,
        'total_dose2': total_dose2,
        'total': total,
    }
    return parsed_data


def _get_pdf_urls():
    html = www.read(URL_VAX_SUMMARY_LIST)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')

    pdf_urls = [
        os.path.join(URL_EPID, a.get('href')[1:]) for a in table.find_all('a')
    ]
    log.info('Found %d PDFs', len(pdf_urls))
    return pdf_urls


def _get_date_id(pdf_url):
    re_data = re.search(REGEX_DATE_ID, pdf_url)
    if not re_data:
        return None
    (y_str, m_str, d_str) = ds.dict_get(
        re_data.groupdict(),
        ['y_str', 'm_str', 'd_str'],
    )
    return '%s%s%s' % (y_str, m_str, d_str)


def _download_parse_single(pdf_url):
    date_id = _get_date_id(pdf_url)
    if date_id is None:
        return

    pdf_file = '/tmp/covid19.epid.vaxs.%s.pdf' % (date_id)
    if not os.path.exists(pdf_file):
        www.download_binary(pdf_url, pdf_file)
    log.info('Downloaded %s to %s', pdf_url, pdf_file)

    tables = _utils.extract_pdf_tables(pdf_file)
    parsed_data = _parse_data_format(date_id, tables)

    date_id = pdf_file[-12:-4]
    ut = timex.parse_time(date_id, '%Y%m%d')
    parsed_data['date_id'] = date_id
    parsed_data['ut'] = ut
    log.info(json.dumps(parsed_data, indent=2))
    return pdf_file, parsed_data


def _dump_single(pdf_file, parsed_data):
    json_file = pdf_file.replace('.pdf', '.json')
    jsonx.write(json_file, parsed_data)
    log.info('Dumped parsed data to %s\n...', json_file)
    return parsed_data


def _validate(parsed_data_list):
    oldest_parsed_data = parsed_data_list[-1]
    (
        covishield_dose1,
        covishield_dose2,
        sinopharm_dose1,
        sinopharm_dose2,
        sputnik_dose1,
        sputnik_dose2,
        pfizer_dose1,
        total_dose1,
        total_dose2,
        total,
        date_id,
        ut,
    ) = oldest_parsed_data.values()

    if covishield_dose1 < covishield_dose2:
        raise Exception('covishield_dose1 < covishield_dose2')

    if sinopharm_dose1 < sinopharm_dose2:
        raise Exception('sinopharm_dose1 < sinopharm_dose2')

    if sputnik_dose1 < sputnik_dose2:
        raise Exception('sputnik_dose1 < sputnik_dose2')

    next_parsed_data = None
    for parsed_data in parsed_data_list:
        if next_parsed_data:
            if parsed_data['total_dose1'] > next_parsed_data['total_dose1']:
                raise Exception('total_dose1 < next.total_dose1')
            if parsed_data['total_dose2'] > next_parsed_data['total_dose2']:
                raise Exception('total_dose2 < next.total_dose2')
            if parsed_data['total'] > next_parsed_data['total']:
                raise Exception('total < next.total')

        next_parsed_data = parsed_data


def _dump_back_pop():
    pdf_urls = _get_pdf_urls()
    parsed_data_list = []
    for pdf_url in pdf_urls:
        pdf_file, parsed_data = _download_parse_single(pdf_url)
        parsed_data_list.append(parsed_data)
        _validate(parsed_data_list)
        _dump_single(pdf_file, parsed_data)


def _dump():
    current_ut = timex.get_unixtime() - timex.SECONDS_IN.DAY
    current_date_id = timex.get_date_id(current_ut)
    pdf_urls = _get_pdf_urls()
    for pdf_url in pdf_urls:
        date_id = _get_date_id(pdf_url)
        if date_id == current_date_id:
            pdf_file, parsed_data = _download_parse_single(pdf_url)
            _dump_single(pdf_file, parsed_data)
            return
    log.warn('Could not find data for %s', current_date_id)


def _dump_summary():
    start_ut = timex.parse_time('2021-01-29', '%Y-%m-%d')
    end_ut = timex.get_unixtime() - timex.SECONDS_IN.DAY  # current

    data_list = []
    prev_parsed_data = None
    for ut in range(start_ut, end_ut, timex.SECONDS_IN.DAY):
        date_id = timex.get_date_id(ut)
        json_file = '/tmp/covid19.epid.vaxs.%s.json' % (date_id)

        if os.path.exists(json_file):
            parsed_data = jsonx.read(json_file)
        else:
            url = os.path.join(
                'https://raw.githubusercontent.com/nuuuwan/covid19',
                'data/covid19.epid.vaxs.%s.json' % (date_id),
            )
            log.info('Downloading data from %s', url)
            parsed_data = www.read_json(url)
            if parsed_data is not None:
                jsonx.write(json_file, parsed_data)

        if parsed_data is None:
            log.warn('No/incorrect data for %s', date_id)
            parsed_data = prev_parsed_data

        log.info(
            'Loaded data for %s (%d vaccinations)',
            date_id,
            parsed_data['total'],
        )
        data_list.append(parsed_data)
        prev_parsed_data = parsed_data

    expanded_data_list = []
    prev_expanded_d = None
    for d in data_list:
        ut = d['ut']
        date = timex.format_time(ut, '%Y-%m-%d')
        expanded_d = {
            'ut': ut,
            'date': date,
        }

        for k in [
            'covishield_dose1',
            'covishield_dose2',
            'sinopharm_dose1',
            'sinopharm_dose2',
            'sputnik_dose1',
            'sputnik_dose2',
            'pfizer_dose1',
            'total_dose1',
            'total_dose2',
            'total',
        ]:
            expanded_d['cum_%s' % k] = d[k]
            prev_v = 0
            if prev_expanded_d:
                prev_v = prev_expanded_d['cum_%s' % k]
            expanded_d['new_%s' % k] = d[k] - prev_v

        expanded_data_list.append(expanded_d)
        prev_expanded_d = expanded_d

    tsv_file = '/tmp/covid19.epid.vaxs.latest.tsv' % (expanded_data_list)
    tsv.write(tsv_file, expanded_data_list)
    log.info('Wrote %d records to %s', len(expanded_data_list), tsv_file)


@cache('covid19', timex.SECONDS_IN.HOUR)
def load_timeseries():
    url = os.path.join(
        'https://raw.githubusercontent.com/nuuuwan/covid19',
        'data/covid19.epid.vaxs.latest.tsv',
    )

    def _clean(d):
        cleaned_d = {}
        for k, v in d.items():
            if k != 'date':
                cleaned_v = (int)(v)
            else:
                cleaned_v = v
            cleaned_d[k] = cleaned_v
        return cleaned_d

    data_list = www.read_tsv(url)
    return [_clean(d) for d in data_list]
