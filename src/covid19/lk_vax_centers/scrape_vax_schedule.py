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

from utils import www

from covid19._utils import log
from covid19.lk_vax_centers import lk_vax_center_utils

TENTATIVE_VAX_SCH_URL = os.path.join(
    'http://www.health.gov.lk',
    'moh_final/english/public/elfinder/files/feturesArtical/2021',
    'Tentative%20vaccination%20schedule%2020.08.2021.xlsx',
)


def scrape_tentative_vax_schedule():
    schedule_file = lk_vax_center_utils.get_file('latest', 'schedule.xlsx')
    www.download_binary(TENTATIVE_VAX_SCH_URL, schedule_file)
    log.info(f'Downloaded {TENTATIVE_VAX_SCH_URL} to {schedule_file}')


if __name__ == '__main__':
    scrape_tentative_vax_schedule()
