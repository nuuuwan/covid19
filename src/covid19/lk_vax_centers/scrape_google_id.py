import logging
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from covid19._utils import log

logging.getLogger('pdfminer').setLevel(logging.ERROR)
logging.getLogger('camelot').setLevel(logging.ERROR)

VAX_DASH_URL = (
    'https://www.presidentsoffice.gov.lk/index.php/vaccination-dashboard/'
)
URL_LOAD_TIME = 10
CACHE_NAME = 'covid19.lk_vax_centers'


def scrape_google_id():
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

if __name__ == '__main__':
    scrape_google_id()
