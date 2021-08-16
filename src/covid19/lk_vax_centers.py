import argparse
import io
import time
import os
import json

from tabula import read_pdf
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from utils import tsv, timex, filex

from covid19._utils import log

VAX_DASH_URL = (
    'https://www.presidentsoffice.gov.lk/index.php/vaccination-dashboard/'
)
URL_LOAD_TIME = 10
I_VAX_CENTER = -3


def get_file(tag, ext):
    return f'/tmp/covid19.lk_vax_centers.{tag}.{ext}'


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
    browser.set_window_size(2000, 2000)

    time.sleep(URL_LOAD_TIME)

    el_iframe = browser.find_element_by_tag_name('iframe')
    url_powerbi = el_iframe.get_attribute('src')
    log.info(f'POWERBI URL = {url_powerbi}')
    browser.switch_to.frame(el_iframe)
    log.info(f'Switched to {browser.current_url}')

    el_buttons = browser.find_elements_by_tag_name('button')
    log.info(f'Found {len(el_buttons)} possible buttons')

    screenshot_file = get_file('latest', 'png')
    browser.save_screenshot(screenshot_file)

    google_drive_file_id = None
    for el_button in el_buttons:
        if el_button.text == 'VACCINATION CENTERS OPEN TODAY':
            el_button.click()

            time.sleep(URL_LOAD_TIME)
            browser.switch_to.window(browser.window_handles[1])
            log.info(f'Switched to {browser.current_url}')
            tokens = browser.current_url.split('/')
            google_drive_file_id = tokens[-2]
            break

    browser.quit()
    log.info(f'google_drive_file_id = {google_drive_file_id}')
    return google_drive_file_id


def scrape():
    pdf_file = get_file('latest', 'pdf')
    if os.path.exists(pdf_file):
        log.warning(f'{pdf_file} already exists. Not scraping!')
        return

    file_id = get_google_drive_file_id()
    google_drive_api_key = get_google_drive_api_key()
    if google_drive_api_key is None:
        log.error('No google_drive_api_key. Aborting.')
        return

    drive_service = build(
        'drive',
        'v3',
        developerKey=google_drive_api_key,
    )
    request = drive_service.files().get_media(fileId=file_id)
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


def is_number(s):
    try:
        x = float(s)
    except:
        return False
    return True

def parse():
    pdf_file = get_file('latest', 'pdf')
    if not os.path.exists(pdf_file):
        log.error(f'{pdf_file} does not exist!')
        return []

    dfs = read_pdf(pdf_file, pages="all")
    data_list = []
    for df in dfs:
        rows = df.values.tolist()
        for row in rows:
            row = list(filter(
                lambda cell: str(cell) != 'nan' and not is_number(cell),
                row,
            ))
            print(row)

            district_name, police_area, center_name = None, None, None
            if len(row) == 3:
                [district_name, police_area, center_name] = row

            elif len(row) == 1:
                [cell_value] = row
                n_words = len(cell_value.split(' '))
                if n_words > 1 or cell_value == cell_value.upper():
                    center_name = cell_value
                else:
                    police_area = cell_value

            elif len(row) == 2:
                [police_area, center_name] = row



            data = dict(
                district_name=district_name,
                police_area=police_area,
                center_name=center_name,
            )
            print(json.dumps(data, indent=2))
            print('-' * 32)

            data_list.append(data)
        #     if len(data_list) > 10:
        #         break
        #
        # if len(data_list) > 10:
        #     break

    n_centers = len(data_list)

    tsv_file = get_file('latest', 'tsv')
    tsv.write(tsv_file, data_list)
    log.info(f'Wrote {n_centers} center info to {tsv_file}')

    return data_list

def dump_summary(data_list):
    md_lines = ['# Open Vaccinations Centers', '']
    prev_district_name = None
    for data in data_list:
        district_name = data['district_name']
        center_name = data['center_name']

        if district_name != prev_district_name:
            md_lines.append(f'* {district_name}')
        md_lines.append(f'  * {center_name}')

        prev_district_name = district_name
    md_file = get_file('latest', 'md')
    md = '\n'.join(md_lines)
    filex.write(md_file, md)
    log.info(f'Wrote summary to {md_file}')


if __name__ == '__main__':
    # scrape()
    data_list = parse()
    # dump_summary(data_list)
