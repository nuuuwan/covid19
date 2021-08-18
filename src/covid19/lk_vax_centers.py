import argparse
import io
import time
import os
import json
import camelot
import logging
import pandas
import re
import googlemaps

import matplotlib.pyplot as plt

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from deep_translator import GoogleTranslator


from utils import tsv, timex, filex


from utils.cache import cache

from covid19._utils import log


logging.getLogger('pdfminer').setLevel(logging.ERROR)
logging.getLogger('camelot').setLevel(logging.ERROR)

VAX_DASH_URL = (
    'https://www.presidentsoffice.gov.lk/index.php/vaccination-dashboard/'
)
URL_LOAD_TIME = 10
I_VAX_CENTER = -3
DEFAULT_ZOOM = 15


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

gmaps = googlemaps.Client(key=get_google_drive_api_key())


@cache('covid19.lk_vax_centers', timex.SECONDS_IN.YEAR)
def get_location_info_inner(search_text):
    return gmaps.geocode(search_text)

@cache('covid19.lk_vax_centers.v3', timex.SECONDS_IN.YEAR)
def get_location_info(district, police, center):
    search_text = f'{center}, {district} District, Sri Lanka'
    geocode_results = get_location_info_inner(search_text)

    if len(geocode_results) == 0 or 'Sri Lanka' not in geocode_results[0]['formatted_address']:
        search_text = f'{police} Police Station, Sri Lanka'
        geocode_results = get_location_info_inner(search_text)

    if len(geocode_results) == 0 or 'Sri Lanka' not in geocode_results[0]['formatted_address']:
        return None, None, None

    geocode_result = geocode_results[0]

    lat = geocode_result['geometry']['location']['lat']
    lng = geocode_result['geometry']['location']['lng']
    formatted_address = geocode_result['formatted_address']
    return lat, lng, formatted_address


translator_si = GoogleTranslator(source='english', target='sinhala')
@cache('covid19.lk_vax_centers', timex.SECONDS_IN.YEAR)
def translate_si(text):
    """Translate text."""
    if len(text) <= 3:
        return text
    return translator_si.translate(text)


translator_ta = GoogleTranslator(source='english', target='tamil')
@cache('covid19.lk_vax_centers', timex.SECONDS_IN.YEAR)
def translate_ta(text):
    """Translate text."""
    if len(text) <= 3:
        return text
    return translator_ta.translate(text)


def get_file(tag, ext):
    return f'/tmp/covid19.lk_vax_centers.{tag}.{ext}'



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

def clean_non_alpha(s):
    s = re.sub(r'[^A-Za-z\s]', '', s)
    s = re.sub(r'\s+', ' ', s)
    s = s.strip()
    return s

def parse_basic():
    pdf_file = get_file('latest', 'pdf')
    tables = camelot.read_pdf(pdf_file, pages='all')

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

            if police in ['Kuliyapitiya', 'Nikaweratiya', 'Kurunegala']:
                district = 'Kurunegala'
            if police in ['Mullaitivu']:
                district = 'Mullaitivu'
            if police in ['Adampan']:
                district = 'Mannar'


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
            log.info(f'Basic: {district.upper()}/{police}/{center}')

    tsv_basic_file = get_file('latest', 'basic.tsv')
    tsv.write(tsv_basic_file, data_list)
    n_data_list = len(data_list)
    log.info(f'Wrote {n_data_list} rows to {tsv_basic_file}')

    return data_list

def expand_with_translation_and_location_for_data(data):
    district = data['district']
    police = data['police']
    center = data['center']
    dose1 = data['dose1']
    dose2 = data['dose2']

    district_si = translate_si(district)
    police_si = translate_si(police)
    center_si = translate_si(center)

    district_ta = translate_ta(district)
    police_ta = translate_ta(police)
    center_ta = translate_ta(center)

    lat, lng, formatted_address = get_location_info(
        district,
        police,
        center,
    )

    formatted_address_si, formatted_address_ta = None, None
    if formatted_address:
        formatted_address_si = translate_si(formatted_address)
        formatted_address_ta = translate_ta(formatted_address)

    log.info(f'Expanded: {district.upper()}/{police}/{center}')

    return dict(
        district=district,
        police=police,
        center=center,

        dose1=dose1,
        dose2=dose2,

        lat=lat,
        lng=lng,
        formatted_address=formatted_address,

        district_si=district_si,
        police_si=police_si,
        center_si=center_si,
        formatted_address_si=formatted_address_si,

        district_ta=district_ta,
        police_ta=police_ta,
        center_ta=center_ta,
        formatted_address_ta=formatted_address_ta,
    )



def expand_with_translation_and_location():
    tsv_basic_file = get_file('latest', 'basic.tsv')
    data_list = tsv.read(tsv_basic_file)

    expanded_data_list = list(map(
        expand_with_translation_and_location_for_data,
        data_list,
    ))

    tsv_file = get_file('latest', 'tsv')
    tsv.write(tsv_file, expanded_data_list)
    n_data_list = len(expanded_data_list)
    log.info(f'Wrote {n_data_list} rows to {tsv_file}')
    return expanded_data_list

def dump_summary(lang):
    date = timex.format_time(timex.get_unixtime(), '%Y-%m-%d')
    tsv_file = get_file('latest', 'tsv')
    data_list = tsv.read(tsv_file)

    if lang == 'si':
        title = 'කොවිඩ්19 එන්නත් මධ්‍යස්ථාන'
        warning = 'ස්ථාන පදනම් වී ඇත්තේ ස්වයංක්‍රීය ගූගල් සිතියම් (Google Maps) ' + 'සෙවීම මත වන අතර ඒවා නිවැරදි නොවිය හැකිය.'
    elif lang == 'ta':
        title = 'கோவிட்19 தடுப்பூசி மையங்கள்'
        warning = 'இருப்பிடங்கள் தானியங்கி கூகுள் மேப்ஸ் தேடலை (Google Maps) ' + 'அடிப்படையாகக் கொண்டவை மற்றும் துல்லியமாக இருக்காது.'
    else:
        title = 'COVID19 Vaccinations Centers'
        warning = 'Locations are based on Automated GoogleMaps Search, ' + 'and might be inaccurate.'

    md_lines = [
        f'# {title} ({date})',
        f'*{warning}*',
    ]
    prev_district, prev_police = None, None
    for data in data_list:
        if lang == 'si':
            district = data['district_si']
            police = data['police_si']
            center = data['center_si']
            formatted_address = data['formatted_address_si']
            police_area_str = 'පොලිස් කලාපය'
            district_str = 'දිස්ත්‍රික්කය'
            dose_str = 'මාත්රාව'
        elif lang == 'ta':
            district = data['district_ta']
            police = data['police_ta']
            center = data['center_ta']
            formatted_address = data['formatted_address_ta']
            police_area_str = 'போலீஸ் பகுதி'
            district_str = 'மாவட்டம்'
            dose_str = 'டோஸ்'
        else:
            district = data['district']
            police = data['police']
            center = data['center']
            formatted_address = data['formatted_address']
            police_area_str = 'Police Area'
            district_str = 'District'
            dose_str = 'Dose'

        dose_tokens = []
        if data['dose1'] == 'True':
            dose_tokens.append(f'{dose_str}-1')
        if data['dose2'] == 'True':
            dose_tokens.append(f'{dose_str}-2')
        dose = ', '.join(dose_tokens)
        if dose:
            dose = f' ({dose}) '


        if formatted_address:
            lat = data['lat']
            lng = data['lng']
            link = f'https://www.google.lk/maps/place/{lat}N,{lng}E'
            md_link = f'[{formatted_address}]({link})'
        else:
            md_link = '(Location Unknown)'

        if district != prev_district:
            md_lines.append(f'## {district} {district_str}')
        if police != prev_police:
            md_lines.append(f'* **{police}** {police_area_str}')
        md_lines.append(f'  * {dose}{center} - {md_link} ')

        prev_district, prev_police = district, police


    md_file = get_file('latest', f'{lang}.md')
    md = '\n'.join(md_lines)
    filex.write(md_file, md)
    log.info(f'Wrote summary to {md_file}')

def copy_latest():
    date_id = timex.get_date_id()
    for ext in ['pdf', 'tsv', 'si.md', 'en.md', 'ta.md']:
        old_file = get_file('latest', ext)
        new_file = get_file(date_id, ext)
        os.system('cp "%s" "%s"' % (old_file, new_file))
        log.info(f'Copied {old_file} to {new_file}')


if __name__ == '__main__':
    scrape()
    parse_basic()
    expand_with_translation_and_location()
    dump_summary('en')
    dump_summary('si')
    dump_summary('ta')
    copy_latest()
