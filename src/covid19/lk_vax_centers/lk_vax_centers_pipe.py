from utils import timex

from covid19.lk_vax_centers import metadata
from covid19.lk_vax_centers.expand import expand
from covid19.lk_vax_centers.finalize import finalize
from covid19.lk_vax_centers.parse_pdf import parse_pdf
from covid19.lk_vax_centers.scrape_google_id import scrape_google_id
from covid19.lk_vax_centers.scrape_pdf import scrape_pdf
from covid19.lk_vax_centers.summarise import summarise

if __name__ == '__main__':
    date_id = timex.get_date_id()
    google_drive_file_id = scrape_google_id()

    if scrape_pdf(date_id, google_drive_file_id):
        parse_pdf(date_id)
        # metadata.backpopulate_oneoff(date_id)
        metadata.populate_new(date_id)
        expand(date_id)
        summarise(date_id)
        finalize(date_id)
