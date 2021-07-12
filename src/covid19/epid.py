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


def _parse_data_format1(tables):
    rows = tables[-1]
    combined_row = []
    for row in rows[-3:]:
        for cell in row:
            cell = cell.replace(',', '')
            cell = cell.replace('-', '0')

            cell = re.sub(r'[^0-9\s]', '', cell)
            cell = re.sub(r'\s+', ' ', cell).strip()
            combined_row.append(cell)
    tokens = re.sub(r'\s+', ' ', (' '.join(combined_row))).strip().split(' ')

    if len(tokens) > 6:
        pfizer_dose2 = _parse_int(tokens[0])
        tokens = tokens[1:]
    else:
        pfizer_dose2 = 0

    covidshield_dose1 = _parse_int(tokens[0])
    covidshield_dose2 = _parse_int(tokens[1])
    sinopharm_dose1 = _parse_int(tokens[2])
    sinopharm_dose2 = _parse_int(tokens[3])
    sputnik_dose1 = _parse_int(tokens[4])
    sputnik_dose2 = _parse_int(tokens[5])

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


def _download_parse_single(pdf_url):
    re_data = re.search(REGEX_DATE_ID, pdf_url)
    if not re_data:
        return
    (y_str, m_str, d_str) = ds.dict_get(
        re_data.groupdict(),
        ['y_str', 'm_str', 'd_str'],
    )
    date_id = '%s%s%s' % (y_str, m_str, d_str)
    pdf_file = '/tmp/covid19.epid.vaxs.%s.pdf' % (date_id)
    if not os.path.exists(pdf_file):
        www.download_binary(pdf_url, pdf_file)
    log.info('Downloaded %s to %s', pdf_url, pdf_file)

    tables = _utils.extract_pdf_tables(pdf_file)
    parsed_data = _parse_data_format1(tables)

    date_id = pdf_file[-12:-4]
    ut = timex.parse_time(date_id, '%Y%m%d')
    parsed_data['date_id'] = date_id
    parsed_data['ut'] = ut
    log.info(json.dumps(parsed_data, indent=2))
    return pdf_file, parsed_data


def _dump_single(pdf_file, parsed_data):
    json_file = pdf_file.replace('.pdf', '.json')
    jsonx.write(json_file, parsed_data)
    log.info('Dumped parsed data to %s', json_file)
    return parsed_data


def _validate(parsed_data_list):
    # latest
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


def _dump():
    pdf_urls = _get_pdf_urls()
    if LIMITED_TEST_MODE:
        log.warn('Running _dump_pdfs in LIMITED_TEST_MODE')
        pdf_urls = [pdf_urls[i] for i in range(0, len(pdf_urls), 10)]

    parsed_data_list = []
    for pdf_url in pdf_urls:
        pdf_file, parsed_data = _download_parse_single(pdf_url)
        parsed_data_list.append(parsed_data)
        try:
            _validate(parsed_data_list)
        except Exception:
            log.error('%s: Format not supported - breaking', pdf_url)
            break
        _dump_single(pdf_file, parsed_data)
