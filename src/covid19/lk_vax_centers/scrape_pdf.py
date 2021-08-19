import argparse
import io
import os
import re

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from utils import timex

from covid19._utils import log
from covid19.lk_vax_centers import lk_vax_center_utils


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


def scrape_pdf(google_drive_file_id):
    google_drive_api_key = get_google_drive_api_key()
    if google_drive_api_key is None:
        log.error('No google_drive_api_key. Aborting.')
        return

    drive_service = build(
        'drive',
        'v3',
        developerKey=google_drive_api_key,
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
    date_id = timex.get_date_id(ut)
    log.info(f'date_id = {date_id}')

    pdf_file = lk_vax_center_utils.get_file(date_id, 'pdf')
    if os.path.exists(pdf_file):
        log.warn(f'{pdf_file} already exists. Not downloading.')
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
    return pdf_file


if __name__ == '__main__':
    scrape_pdf('1nQX4ugCIvnNIMGvynIh34zZBorjZMWtf')
