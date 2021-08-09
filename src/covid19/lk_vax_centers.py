import argparse
import io
import os
import time

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from covid19._utils import log

VAX_DASH_URL = os.path.join(
    'https://www.presidentsoffice.gov.lk', 'index.php/vaccination-dashboard/'
)
URL_LOAD_TIME = 10


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
    browser.get(VAX_DASH_URL)
    browser.set_window_size(2000, 2000)

    browser.save_screenshot("/tmp/sel%d.png" % 1)
    time.sleep(URL_LOAD_TIME)
    browser.save_screenshot("/tmp/sel%d.png" % 2)

    el = browser.find_element_by_id("content")
    print(el)
    print(el.size)
    print(el.location)

    action = webdriver.common.action_chains.ActionChains(browser)
    action.move_to_element_with_offset(el, 500, 1200)
    action.click()
    action.perform()

    browser.save_screenshot("/tmp/sel%d.png" % 3)
    time.sleep(URL_LOAD_TIME)
    browser.save_screenshot("/tmp/sel%d.png" % 4)
    print(browser.current_url)

    browser.quit()



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
    # TEST_FILE_ID = '1qro8z-veN1Kd-rv00b4haZPaAHIGuwDs'
    # scrape(TEST_FILE_ID)
    get_google_drive_file_id()
