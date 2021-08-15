import argparse
import io
import time

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from utils import tsv

from covid19._utils import log

VAX_DASH_URL = (
    'https://www.presidentsoffice.gov.lk/index.php/vaccination-dashboard/'
)
URL_LOAD_TIME = 15
I_VAX_CENTER = -3


def get_pdf_file():
    return '/tmp/covid10.lk_vax_centers.pdf'


def get_google_drive_api_key():
    """Construct Twitter from Args."""
    parser = argparse.ArgumentParser(description='lk_vax_centers')
    parser.add_argument(
        '--google_drive_api_key',
        type=str,
        required=False,
        default=None,
    )
    args = parser.parse_args()
    return args.google_drive_api_key


def get_google_drive_file_id():
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)

    log.info('Crawling "%s"', VAX_DASH_URL)
    browser.get(VAX_DASH_URL)
    browser.set_window_size(4000, 4000)

    time.sleep(URL_LOAD_TIME)

    el_iframe = browser.find_element_by_tag_name('iframe')
    url_powerbi = el_iframe.get_attribute('src')
    log.info(f'POWERBI URL = {url_powerbi}')
    browser.switch_to.frame(el_iframe)
    log.info(f'Switched to {browser.current_url}')

    el_buttons = browser.find_elements_by_tag_name('button')
    for el_button in el_buttons:
        log.info(el_buttons)
    log.info(f'Found {len(el_buttons)} possible buttons')
    el_button_vax_center = el_buttons[I_VAX_CENTER]
    el_button_vax_center.click()

    time.sleep(URL_LOAD_TIME)
    browser.switch_to.window(browser.window_handles[1])
    log.info(f'Switched to {browser.current_url}')
    tokens = browser.current_url.split('/')
    browser.quit()

    google_drive_file_id = tokens[-2]
    log.info(f'google_drive_file_id = {google_drive_file_id}')
    return google_drive_file_id


def scrape(file_id):
    google_drive_api_key = get_google_drive_api_key()
    if google_drive_api_key is None:
        log.error('No google_drive_api_key. Aborting.')
        return False

    drive_service = build(
        'drive',
        'v3',
        developerKey=google_drive_api_key,
    )
    request = drive_service.files().get_media(fileId=file_id)
    pdf_file = get_pdf_file()
    fh = io.FileIO(pdf_file, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        log.info(
            'Downloading {file_id} to {pdf_file} ({progress:.1%})'.format(
                file_id=file_id,
                pdf_file=pdf_file,
                progress=(float)(status.progress()),
            )
        )


def parse():
    pdf_file = get_pdf_file()
    from tabula import read_pdf

    dfs = read_pdf(pdf_file, pages="all")
    data_list = []
    for df in dfs:
        rows = df.values.tolist()
        for row in rows:
            (
                district_num,
                district_name,
                center_num,
                police_area,
                center_name,
            ) = row[:5]
            data = dict(
                district_num=district_num,
                district_name=district_name,
                center_num=center_num,
                police_area=police_area,
                center_name=center_name,
            )
            data_list.append(data)

    # fix blanks
    data_list2 = []
    cur_district_name = None
    for data in data_list:
        district_name = str(data['district_name'])

        if district_name in ['Sub Total', '9']:
            cur_district_name = None
        elif district_name == 'Grand Total':
            continue
        elif district_name != 'nan':
            cur_district_name = district_name
            data_list2.append(data)
        else:
            if cur_district_name:
                data['district_name'] = cur_district_name
            data_list2.append(data)
    data_list = data_list2

    data_list2 = []
    cur_district_name = None
    data_list.reverse()
    for data in data_list:
        district_name = str(data['district_name'])
        if district_name != 'nan':
            cur_district_name = district_name
            data_list2.append(data)
        else:
            if cur_district_name:
                data['district_name'] = cur_district_name
            data_list2.append(data)

    data_list2.reverse()
    data_list = data_list2

    n_centers = len(data_list)

    tsv_file = pdf_file.replace('.pdf', '.tsv')
    tsv.write(tsv_file, data_list)
    log.info(f'Wroted {n_centers} center info to {tsv_file}')


if __name__ == '__main__':
    file_id = get_google_drive_file_id()
    scrape(file_id)
    parse()
