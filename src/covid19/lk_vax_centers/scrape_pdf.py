import io
import os
import re

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from utils import timex

from covid19._utils import log
from covid19.lk_vax_centers import (google_utils, lk_vax_center_utils,
                                    scrape_google_id)


def scrape_pdf(date_id):
    pdf_file = lk_vax_center_utils.get_file(date_id, 'pdf')
    if os.path.exists(pdf_file):
        log.warn(f'{pdf_file} already exists. Not downloading.')
        return pdf_file

    google_drive_file_id = scrape_google_id.scrape_google_id()
    if google_drive_file_id is None:
        log.error('Invalid google_drive_file_id. Aborting.')
        return False

    google_api_key = google_utils.get_google_api_key()
    if google_api_key is None:
        log.error('No google_api_key. Aborting.')
        return False

    drive_service = build(
        'drive',
        'v3',
        developerKey=google_api_key,
    )

    request = drive_service.files().get_media(fileId=google_drive_file_id)
    data = drive_service.files().get(fileId=google_drive_file_id).execute()
    file_title = data['name']
    re_result = re.search(r'.*(?P<date_str>\d{2}\.\d{2}\.\d{4}).*', file_title)
    if not re_result:
        log.error(f'Invalid file "{file_title}"')
        return False

    date_str = re_result.groupdict().get('date_str')
    ut = timex.parse_time(date_str, '%d.%m.%Y')
    doc_date_id = timex.get_date_id(ut)
    log.info(f'doc_date_id = {doc_date_id}')

    if doc_date_id != date_id:
        log.error(
            f'Invalid doc_date_id {doc_date_id} (!= {date_id}). Aborting!'
        )
        return False

    fh = io.FileIO(pdf_file, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        log.info(
            'Downloading {file_id} to {pdf_file} ({progress:.1%})'.format(
                file_id=google_drive_file_id,
                pdf_file=pdf_file,
                progress=(float)(status.progress()),
            )
        )
    return True


if __name__ == '__main__':
    scrape_pdf('1nQX4ugCIvnNIMGvynIh34zZBorjZMWtf')
