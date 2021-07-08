"""EPID utils."""
import json
import logging
import os
import re

import tabula
from bs4 import BeautifulSoup
from utils import ds, dt, jsonx, timex, www

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('covid19.epid')

URL_EPID = 'https://www.epid.gov.lk'
URL_VAX_SUMMARY_LIST = os.path.join(
    URL_EPID,
    'web/index.php?',
    'option=com_content&view=article&id=231&lang=en',
)
REGEX_DATE_ID = r'(?P<y_str>\d{4})-(?P<m_str>\d{2})_(?P<d_str>\d{2})'
LIMITED_TEST_MODE = True


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


def _download_parse_and_dump_single(pdf_url):
    re_data = re.search(REGEX_DATE_ID, pdf_url)
    if re_data:
        (y_str, m_str, d_str) = ds.dict_get(
            re_data.groupdict(),
            ['y_str', 'm_str', 'd_str'],
        )
        date_id = '%s%s%s' % (y_str, m_str, d_str)
        pdf_file = '/tmp/covid19.epid.vaxs.%s.pdf' % (date_id)
        if not os.path.exists(pdf_file):
            www.download_binary(pdf_url, pdf_file)
        log.info('Downloaded %s to %s', pdf_url, pdf_file)

        df = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True)[0]
        row_k_to_items = {}
        for _, cell_map in df.to_dict().items():
            for row_k, cell_vallue in cell_map.items():
                if row_k not in row_k_to_items:
                    row_k_to_items[row_k] = []
                row_k_to_items[row_k].append(cell_vallue)
        rows = list(row_k_to_items.values())
        print(rows[-3:])
        combined_row = []
        for i in range(0, len(rows[-1])):
            cell = ''
            for row in rows[-3:]:
                if isinstance(row[i], float):
                    continue
                cell += str(row[i])
            cell = cell.replace(',', '')
            cell = cell.replace('-', '0')

            cell = re.sub(r'[^0-9\s]', '', cell)
            cell = re.sub(r'\s+', ' ', cell).strip()

            combined_row.append(cell)
        print(combined_row)

        tokens = (
            re.sub(r'\s+', ' ', (' '.join(combined_row))).strip().split(' ')
        )

        covidshield_dose1 = _parse_int(tokens[0])
        covidshield_dose2 = _parse_int(tokens[1])
        sinopharm_dose1 = _parse_int(tokens[2])
        sinopharm_dose2 = _parse_int(tokens[3])
        sputnik_dose1 = _parse_int(tokens[4])
        sputnik_dose2 = _parse_int(tokens[5])

        if len(tokens) > 6:
            pfizer_dose2 = _parse_int(tokens[6])
        else:
            pfizer_dose2 = 0

        date_id = pdf_file[-12:-4]
        ut = timex.parse_time(date_id, '%Y%m%d')
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
            'ut': ut,
            'date': timex.format_time(ut, '%Y-%m-%d'),
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
        log.info(json.dumps(parsed_data, indent=2))

        json_file = pdf_file.replace('.pdf', '.json')
        jsonx.write(json_file, parsed_data)
        log.info('Dumped parsed data to %s', json_file)


def _dump():
    pdf_urls = _get_pdf_urls()
    if LIMITED_TEST_MODE:
        log.warn('Running _dump_pdfs in LIMITED_TEST_MODE')
        # pdf_urls = [
        #     pdf_urls[0],
        #     pdf_urls[1],
        #     # pdf_urls[15],
        #     # pdf_urls[16],
        # ]
        pdf_urls = pdf_urls[30:40]

    for pdf_url in pdf_urls:
        _download_parse_and_dump_single(pdf_url)
