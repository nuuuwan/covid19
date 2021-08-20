import logging
import os
import re

import camelot
from utils import timex, tsv

from covid19._utils import log
from covid19.lk_vax_centers import lk_vax_center_utils

logging.getLogger('pdfminer').setLevel(logging.ERROR)
logging.getLogger('camelot').setLevel(logging.ERROR)


def clean_non_alpha(s):
    s = re.sub(r'[^A-Za-z\s]', '', s)
    s = re.sub(r'\s+', ' ', s)
    s = s.strip()
    return s


def parse_pdf(date_id):
    pdf_file = lk_vax_center_utils.get_file(date_id, 'pdf')
    if not os.path.exists(pdf_file):
        log.error(f'{pdf_file} does not exist. Aborting.')
        return False

    tables = camelot.read_pdf(pdf_file, pages='all')
    log.info(f'Found {len(tables)} tables in {pdf_file}')
    data_list = []
    prev_district, prev_police = None, None
    for table in tables:
        rows = table.df.values.tolist()
        for row in rows:
            [serial, district, police1, police2, center] = row
            if serial.lower().strip() == 'serial':
                continue

            police1 = clean_non_alpha(police1)
            police2 = clean_non_alpha(police2)
            police = ''
            if police1:
                police = police1
            elif police2:
                police = police2

            if police in ['Kotmale']:
                district = 'Nuwara Eliya'
            if police in ['Mullaitivu']:
                district = 'Mullaitivu'
            if police in ['Kilinochchi']:
                district = 'Kilinochchi'
            if police in ['Adampan']:
                district = 'Mannar'

            if police in ['Valachchenai']:
                district = 'Batticaloa'

            if police in ['Kuliyapitiya', 'Nikaweratiya', 'Kurunegala']:
                district = 'Kurunegala'
            if police in ['Chilaw']:
                district = 'Puttalam'


            if not district and prev_district:
                district = prev_district

            if not police and prev_police:
                police = prev_police

            if district:
                prev_district = district
            if police:
                prev_police = police

            if len(center) <= 3:
                continue

            dose1, dose2 = False, False
            if '1st Dose' in center:
                dose1 = True
            if '2nd Dose' in center:
                dose2 = True
            center = center.partition('(')[0].strip()

            data = dict(
                district=district,
                police=police,
                center=center,
                dose1=dose1,
                dose2=dose2,
            )
            data_list.append(data)

    tsv_basic_file = lk_vax_center_utils.get_file(date_id, 'basic.tsv')
    tsv.write(tsv_basic_file, data_list)
    n_data_list = len(data_list)
    log.info(f'Wrote {n_data_list} rows to {tsv_basic_file}')
    return data_list


if __name__ == '__main__':
    date_id = timex.get_date_id()
    parse_pdf(date_id)
