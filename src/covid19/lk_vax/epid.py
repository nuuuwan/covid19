"""EPID utils."""
import json
import logging
import os
import re

from bs4 import BeautifulSoup
from tablex import extract
from utils import ds, dt, jsonx, timex, tsv, www
from utils.cache import cache

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('covid19.epid')
logging.getLogger("pdfminer").setLevel(logging.WARNING)

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
        return '20210908'
    (y_str, m_str, d_str) = ds.dict_get(
        re_data.groupdict(),
        ['y_str', 'm_str', 'd_str'],
    )
    date_id = '%s%s%s' % (y_str, m_str, d_str)
    if date_id == '20210908':
        return '20210907'
    return date_id


def _download_parse_single(pdf_url):
    date_id = _get_date_id(pdf_url)
    if date_id is None:
        return

    pdf_file = '/tmp/covid19.epid.vaxs.%s.pdf' % (date_id)
    if not os.path.exists(pdf_file):
        www.download_binary(pdf_url, pdf_file)
    log.info('Downloaded %s to %s', pdf_url, pdf_file)

    csv_file = '/tmp/covid19.epid.vaxs.%s.csv' % (date_id)
    extract.pdf_to_csv(pdf_file, csv_file)
    json_file = '/tmp/covid19.epid.vaxs.%s.json' % (date_id)
    extract.csv_to_json(csv_file, json_file)

    data_list = jsonx.read(json_file)

    if date_id > '2021-05-05':
        last_data = data_list[-1]
        parsed_data = {
            'covishield_dose1': last_data.get('Covishield.FirstDose', 0),
            'covishield_dose2': last_data.get('Covishield.SecondDose', 0),
            'sinopharm_dose1': last_data.get('Sinopharm.FirstDose', 0),
            'sinopharm_dose2': last_data.get('Sinopharm.SecondDose', 0),
            'sputnik_dose1': last_data.get('Sputnik.FirstDose', 0),
            'sputnik_dose2': last_data.get('Sputnik.SecondDose', 0),
            'pfizer_dose1': last_data.get('Pfizer.FirstDose', 0),
            'pfizer_dose2': last_data.get('Pfizer.SecondDose', 0),
            'moderna_dose1': last_data.get('Moderna.FirstDose', 0),
            'moderna_dose2': last_data.get('Moderna.SecondDose', 0),
        }
    else:
        parsed_data = {}

    parsed_data['total_dose1'] = sum(
        [
            parsed_data.get('covishield_dose1', 0),
            parsed_data.get('sinopharm_dose1', 0),
            parsed_data.get('sputnik_dose1', 0),
            parsed_data.get('pfizer_dose1', 0),
            parsed_data.get('moderna_dose1', 0),
        ]
    )

    parsed_data['total_dose2'] = sum(
        [
            parsed_data.get('covishield_dose2', 0),
            parsed_data.get('sinopharm_dose2', 0),
            parsed_data.get('sputnik_dose2', 0),
            parsed_data.get('pfizer_dose2', 0),
            parsed_data.get('moderna_dose2', 0),
        ]
    )

    parsed_data['total'] = sum(
        [
            parsed_data['total_dose1'],
            parsed_data['total_dose2'],
        ]
    )

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
    next_parsed_data = None
    for parsed_data in parsed_data_list:
        (
            covishield_dose1,
            covishield_dose2,
            sinopharm_dose1,
            sinopharm_dose2,
            sputnik_dose1,
            sputnik_dose2,
            pfizer_dose1,
            pfizer_dose2,
            moderna_dose1,
            moderna_dose2,
            total_dose1,
            total_dose2,
            total,
        ) = (
            parsed_data.get('covishield_dose1', 0),
            parsed_data.get('covishield_dose2', 0),
            parsed_data.get('sinopharm_dose1', 0),
            parsed_data.get('sinopharm_dose2', 0),
            parsed_data.get('sputnik_dose1', 0),
            parsed_data.get('sputnik_dose2', 0),
            parsed_data.get('pfizer_dose1', 0),
            parsed_data.get('pfizer_dose2', 0),
            parsed_data.get('moderna_dose1', 0),
            parsed_data.get('moderna_dose2', 0),
            parsed_data.get('total_dose1', 0),
            parsed_data.get('total_dose2', 0),
            parsed_data.get('total', 0),
        )

        if covishield_dose1 < covishield_dose2:
            raise Exception('covishield_dose1 < covishield_dose2')

        if sinopharm_dose1 < sinopharm_dose2:
            raise Exception('sinopharm_dose1 < sinopharm_dose2')

        if sputnik_dose1 < sputnik_dose2:
            raise Exception('sputnik_dose1 < sputnik_dose2')

        if pfizer_dose1 < pfizer_dose2:
            raise Exception('pfizer_dose1 < pfizer_dose2')

        if moderna_dose1 < moderna_dose2:
            raise Exception('moderna_dose1 < moderna_dose2')

        if total_dose1 < total_dose2:
            raise Exception('total_dose1 < total_dose2')

        if total < total_dose1:
            raise Exception('total < total_dose1')

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

    _validate(reversed(data_list))

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
            'pfizer_dose2',
            'moderna_dose1',
            'moderna_dose2',
            'total_dose1',
            'total_dose2',
            'total',
        ]:
            expanded_d['cum_%s' % k] = d.get(k, 0)
            prev_v = 0
            if prev_expanded_d:
                prev_v = prev_expanded_d.get('cum_%s' % k, 0)
            expanded_d['new_%s' % k] = d.get(k, 0) - prev_v

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
