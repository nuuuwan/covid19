import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from covid19._utils import log

VAX_DASH_URL = (
    'https://www.presidentsoffice.gov.lk/index.php/vaccination-dashboard/'
)
URL_LOAD_TIME = 10


def scrape_google_id():
    options = Options()
    options.headless = True

    driver = webdriver.Firefox(options=options)

    log.info('Crawling "%s"', VAX_DASH_URL)
    driver.get(VAX_DASH_URL)
    driver.set_window_size(1000, 3000)

    time.sleep(URL_LOAD_TIME)

    el_iframe = driver.find_element_by_tag_name('iframe')
    url_powerbi = el_iframe.get_attribute('src')
    log.info(f'POWERBI URL = {url_powerbi}')
    driver.switch_to.frame(el_iframe)
    log.info(f'Switched to {driver.current_url}')

    div_vax_center = driver.find_element_by_xpath(
        '//*[text()="VACCINATION CENTERS OPEN TODAY"]'
    )

    google_drive_file_id = None
    if div_vax_center:
        webdriver.ActionChains(driver).move_to_element(div_vax_center).click(
            div_vax_center
        ).perform()
        time.sleep(URL_LOAD_TIME)

        driver.switch_to.window(driver.window_handles[1])
        log.info(f'Switched to {driver.current_url}')
        tokens = driver.current_url.split('/')
        google_drive_file_id = tokens[-2]

    driver.quit()
    log.info(f'google_drive_file_id = {google_drive_file_id}')
    return google_drive_file_id


if __name__ == '__main__':
    scrape_google_id()
