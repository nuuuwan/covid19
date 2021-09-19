import sys

from utils import timex

from covid19.lk_vax_centers.expand import expand
from covid19.lk_vax_centers.expand_i18n import expand_i18n
from covid19.lk_vax_centers.finalize import finalize
from covid19.lk_vax_centers.parse_pdf import parse_pdf
from covid19.lk_vax_centers.scrape_pdf import scrape_pdf
from covid19.lk_vax_centers.summarise import summarise

if __name__ == '__main__':
    date_id = timex.get_date_id()
    if not scrape_pdf(date_id):
        sys.exit(-1)
    parse_pdf(date_id)
    expand(date_id)
    expand_i18n(date_id)
    summarise(date_id)
    finalize(date_id)
    sys.exit(0)
