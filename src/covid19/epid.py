"""EPID utils."""
import logging
import os
import re

from bs4 import BeautifulSoup
from utils import ds, www

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('covid19.epid')

URL_EPID = 'https://www.epid.gov.lk'
URL_VAX_SUMMARY_LIST = os.path.join(
    URL_EPID,
    'web/index.php?',
    'option=com_content&view=article&id=231&lang=en',
)
REGEX_DATE_ID = r'(?P<y_str>\d{4})-(?P<m_str>\d{2})_(?P<d_str>\d{2})'


def _get_pdf_urls():
    html = www.read(URL_VAX_SUMMARY_LIST)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')

    pdf_urls = [
        os.path.join(URL_EPID, a.get('href')[1:]) for a in table.find_all('a')
    ]
    log.info('Found %d PDFs', len(pdf_urls))
    return pdf_urls


def _dump_pdfs():
    pdf_urls = _get_pdf_urls()
    for pdf_url in pdf_urls[:5]:
        re_data = re.search(REGEX_DATE_ID, pdf_url)
        if re_data:
            (y_str, m_str, d_str) = ds.dict_get(
                re_data.groupdict(),
                ['y_str', 'm_str', 'd_str'],
            )
            date_id = '%s%s%s' % (y_str, m_str, d_str)
            pdf_file = '/tmp/covid19.epid.vaxs.%s.pdf' % (date_id)
            www.download_binary(pdf_url, pdf_file)
            log.info('Downloaded %s to %s', pdf_url, pdf_file)


if __name__ == '__main__':
    _dump_pdfs()
