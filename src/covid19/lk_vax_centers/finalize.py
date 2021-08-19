import os
from utils import timex
from covid19._utils import log
from covid19.lk_vax_centers import lk_vax_center_utils


def finalize(date_id):
    for ext in ['pdf', 'basic.tsv', 'tsv', 'si.md', 'en.md', 'ta.md']:
        from_file = lk_vax_center_utils.get_file(date_id, ext)
        if not os.path.exists(from_file):
            log.warn(f'{from_file} does not exist..')
            continue

        to_file = lk_vax_center_utils.get_file('latest', ext)
        os.system('cp "%s" "%s"' % (from_file, to_file))
        log.info(f'Copied {from_file} to {to_file}')


if __name__ == '__main__':
    date_id = timex.get_date_id()
    finalize(date_id)
