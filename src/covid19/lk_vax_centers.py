import argparse
import io
import os
import time

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


from utils import filex
from covid19._utils import log


POWER_BI_ID = 'eyJrIjoiODY1MTliZjQtNTMzNi00MmRmLTg4NDMtM2U5YWZkMWMwNjNlIiwidCI6ImExNzJkODM2LWQ0YTUtNDBjZS1hNGFkLWJiY2FhMTAzOGY1NiIsImMiOjEwfQ%3D%3D'
VAX_DASH_URL = 'https://app.powerbi.com/view?r=%s' % POWER_BI_ID
URL_LOAD_TIME = 10
I_VAX_CENTER = 20


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
    options.headless = False

    browser = webdriver.Firefox(options=options)
    browser.get(VAX_DASH_URL)
    browser.set_window_size(2000, 2000)

    time.sleep(10)
    els = browser.find_elements_by_tag_name('button')
    el_vax_center = els[I_VAX_CENTER]
    el_vax_center.click()

    time.sleep(10)
    browser.switch_to.window(browser.window_handles[1])
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
    pdf_file = '/tmp/covid10.lk_vax_centers.pdf'
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


if __name__ == '__main__':
    file_id = get_google_drive_file_id()
    scrape(file_id)
