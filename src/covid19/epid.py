"""EPID utils."""
import json
import logging
import os
import re

from bs4 import BeautifulSoup
from utils import ds, dt, jsonx, timex, www

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
        if len(row_3) == 6:
            row_pfizer = (
                _utils._row_to_ints(rows[-4])
                + _utils._row_to_ints(rows[-5])
                + _utils._row_to_ints(rows[-2])
            )
        elif len(row_3) == 7:
            row_pfizer = [row_3[-1]]
            row_3 = row_3[:-1]
        else:
            row_3 = _utils._row_to_ints(rows[-2])
            row_pfizer = []
        pfizer_dose2 = row_pfizer[0] if row_pfizer else 0

        (
            covidshield_dose1,
            covidshield_dose2,
            sinopharm_dose1,
            sinopharm_dose2,
            sputnik_dose1,
            sputnik_dose2,
        ) = row_3

        if sinopharm_dose2 == 2435:
            sinopharm_dose2 = 0
    elif date_id > '20210129':
        covidshields = []
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
                covidshields.append(dt.parse_int(row_new[1]))
            if len(row_new) >= 4:
                sinopharms.append(dt.parse_int(row_new[3]))
        covidshield_dose1 = max(covidshields)
        covidshield_dose2 = covidshields[-1]
        if covidshield_dose2 >= covidshield_dose1:
            covidshield_dose2 = 0
        sinopharm_dose1 = max(sinopharms) if sinopharms else 0
        if sinopharm_dose1 == 246:
            sinopharm_dose1 = 2469

        sinopharm_dose2 = 0
        sputnik_dose1 = 0
        sputnik_dose2 = 0
        pfizer_dose2 = 0
    else:
        covidshield_dose1 = 5286
        covidshield_dose2 = 0
        sinopharm_dose1 = 0
        sinopharm_dose2 = 0
        sputnik_dose1 = 0
        sputnik_dose2 = 0
        pfizer_dose2 = 0

    total_dose1 = sum(
        [
            covidshield_dose1,
            sinopharm_dose1,
            sputnik_dose1,
        ]
    )
    total_dose2 = sum(
        [
            covidshield_dose2,
            sinopharm_dose2,
            sputnik_dose2,
            pfizer_dose2,
        ]
    )
    total = sum(
        [
            total_dose1,
            total_dose2,
        ]
    )

    parsed_data = {
        'covidshield_dose1': covidshield_dose1,
        'covidshield_dose2': covidshield_dose2,
        'sinopharm_dose1': sinopharm_dose1,
        'sinopharm_dose2': sinopharm_dose2,
        'sputnik_dose1': sputnik_dose1,
        'sputnik_dose2': sputnik_dose2,
        'pfizer_dose2': pfizer_dose2,
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
        covidshield_dose1,
        covidshield_dose2,
        sinopharm_dose1,
        sinopharm_dose2,
        sputnik_dose1,
        sputnik_dose2,
        pfizer_dose2,
        total_dose1,
        total_dose2,
        total,
        date_id,
        ut,
    ) = oldest_parsed_data.values()

    if covidshield_dose1 < covidshield_dose2:
        raise Exception('covidshield_dose1 < covidshield_dose2')

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
