"""Pull covid data from various online sources."""

from utils import www

JHU_URL = 'https://pomber.github.io/covid19/timeseries.json'
HPB_URL = 'https://www.hpb.health.gov.lk/api/get-current-statistical'


def load_jhu_data():
    """Pull data from JHU's CSSE.

    COVID-19 Data Repository by the Center for Systems Science and Engineering
    (CSSE) at Johns Hopkins University.

    Source: https://pomber.github.io/covid19/timeseries.json via
        https://github.com/CSSEGISandData/COVID-19
    """
    return www.read_json(JHU_URL)


def load_hpb_data():
    """Pull data from HPB.

    Health Promotion Bureau of Sri Lanka.

    Source: https://www.hpb.health.gov.lk/api/get-current-statistical
    """
    return www.read_json(HPB_URL)
