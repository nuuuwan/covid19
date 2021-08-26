"""
Ministry of health seems to have the type
http://health.gov.lk/moh_final/english/news_read_more.php?id=977

@icta_srilanka
 has a link
https://vaccine.covid19.gov.lk/sign-in, but it's not updated.

I remember
@Sri_Lanka_Army
 having one, but can't seem to find it.
"""
import os

import pandas
from bs4 import BeautifulSoup

from gig import ents
from utils import tsv, www

from covid19._utils import log
from covid19.lk_vax_centers import lk_vax_center_utils

DIR_DATA_LK_VAX_SCHEDULE = '/tmp/covid19/lk_vax_schedule'

TENTATIVE_VAX_SCH_URL = os.path.join(
    'http://www.health.gov.lk',
    'moh_final/english/public/elfinder/files/feturesArtical/2021',
    'Tentative%20vaccination%20schedule%2020.08.2021.xlsx',
)

def make_data_dir():
    os.system(f'mkdir -p {DIR_DATA_LK_VAX_SCHEDULE}')

def scrape_xlsx_file_url():
    URL = 'http://health.gov.lk/moh_final/english/news_read_more.php?id=977'
    html = www.read(URL)
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a'):
        href = a.get('href')
        if 'xlsx' in href:
            return href
    return None


def scrape_tentative_vax_schedule(xlsx_file_url):
    make_data_dir()
    schedule_xlsx_file = os.path.join(
        DIR_DATA_LK_VAX_SCHEDULE,
        'schedule.latest.xlsx',
    )
    www.download_binary(xlsx_file_url, schedule_xlsx_file)
    log.info(f'Downloaded {xlsx_file_url} to {schedule_xlsx_file}')

    data_frame = pandas.read_excel(
        schedule_xlsx_file,
    )
    data_frame = data_frame.fillna(method='ffill', axis=0)

    data_list = []
    prev_row = None
    prev_gnd = None
    for row in data_frame.values.tolist():
        if str(row[1]) == 'nan' or str(row[1]) == 'Province':
            continue
        if str(row) == str(prev_row):
            continue
        __, province, district, moh, gnd, center, vaccine = row
        if gnd == 'GN area':
            gnd = ''

        district = district.strip()

        province_ents = ents.get_entities_by_name_fuzzy(province, 'province')
        province_id = None
        if province_ents:
            province_ent = province_ents[0]
            province_id = province_ent['id']
            province = province_ent['name']

        if district in ['Colombo RDHS', 'CMC']:
            district_id = 'LK-11'
        elif district in ['Kalutara NIHS']:
            district_id = 'LK-13'
        else:
            district_ents = ents.get_entities_by_name_fuzzy(
                district,
                filter_entity_type='district',
                filter_parent_id=province_id,
            )
            district_id = None
            if district_ents:
                district_ent = district_ents[0]
                district_id = district_ent['id']
                district = district_ent['name']

        moh_ents = ents.get_entities_by_name_fuzzy(
            moh, filter_entity_type='moh'
        )
        moh_id = None
        if moh_ents:
            moh_ent = moh_ents[0]
            moh_id = moh_ent['id']
            moh = moh_ent['name']

        gnd_ents = ents.get_entities_by_name_fuzzy(
            gnd, filter_entity_type='gnd', filter_parent_id=district_id
        )
        gnd_id = None
        if gnd_ents:
            gnd_ent = gnd_ents[0]
            gnd_id = gnd_ent['id']
            gnd = gnd_ent['name']

        if gnd == prev_gnd:
            gnd = ''
            gnd_id = None
        else:
            prev_gnd = gnd

        data = dict(
            province=province,
            province_id=province_id,
            district=district,
            district_id=district_id,
            moh=moh,
            moh_id=moh_id,
            gnd=gnd,
            gnd_id=gnd_id,
            center=center,
            vaccine=vaccine,
        )
        data_list.append(data)
        prev_row = row

    schedule_tsv_file = os.path.join(
        DIR_DATA_LK_VAX_SCHEDULE,
        'schedule.latest.tsv',
    )
    tsv.write(schedule_tsv_file, data_list)
    log.info(f'Wrote {len(data_list)} to {schedule_tsv_file}')


def analyze():
    schedule_tsv_file = lk_vax_center_utils.get_file('latest', 'schedule.tsv')
    data_list = tsv.read(schedule_tsv_file)
    district_to_vaccine_to_count = {}
    for data in data_list:
        district = data['district']
        vaccine = data['vaccine']

        if district not in district_to_vaccine_to_count:
            district_to_vaccine_to_count[district] = {}
        if vaccine not in district_to_vaccine_to_count[district]:
            district_to_vaccine_to_count[district][vaccine] = 0
        district_to_vaccine_to_count[district][vaccine] += 1

    for district, vaccine_to_count in district_to_vaccine_to_count.items():
        print(district)
        for vaccine, count in vaccine_to_count.items():
            print('\t', vaccine, ' (', count, 'centers)'),


if __name__ == '__main__':
    xlsx_file_url = scrape_xlsx_file_url()
    scrape_tentative_vax_schedule(xlsx_file_url)
    analyze()
