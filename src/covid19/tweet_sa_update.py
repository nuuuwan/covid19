"""Example Tweet."""
import logging

from utils import twitter
from covid19 import covid_data
from covid19.plots import _plot_south_asia

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('covid19.twitter')


def _get_country_label(country_id):
    return {
        'LK': '🇱🇰 #SriLanka',
        'IN': '🇮🇳 #India',
        'PK': '🇵🇰 #Pakistan',
        'NP': '🇳🇵 #Nepal',
        'BD': '🇧🇩 #Bangladesh',
        'AF': '🇦🇫 #Afghanistan',
        'MV': '🇲🇻 #Maldives',
        'BT': '🇧🇹 #Bhutan',
    }.get(country_id, '')


def _get_tweet_text(max_country_ids):
    jhu_data = covid_data.load_jhu_data()
    _ds = jhu_data['LK']['timeseries'][-1]['date'][:10]

    return '''
#COVID19 #SouthAsia {_ds}

🔴 Active COVID19 Cases - {max0}
🔴 Daily COVID19 Deaths - {max1}
🟢 Daily Vaccinations - {max2}
🟢 People Fully Vaxed - {max3}

14-day avg. per 100K peo.
Excl. #Maldives & #Bhutan

@JHUSystems @OurWorldInData #lka
    '''.format(
        _ds=_ds,
        max0=_get_country_label(max_country_ids[0]),
        max1=_get_country_label(max_country_ids[1]),
        max2=_get_country_label(max_country_ids[2]),
        max3=_get_country_label(max_country_ids[3]),
    )


def _plot_images():
    plot_info_list = [
        _plot_south_asia(
            'active',
            'Active COVID19 Cases',
            lambda x, p: format(int(x), ','),
        ),
        _plot_south_asia(
            'new_deaths',
            'New Daily COVID19 Deaths',
            lambda x, p: format(float(x), '.2'),
        ),
        _plot_south_asia(
            'new_vaccinations',
            'New Daily Vaccinations',
            lambda x, p: format(int(x), ','),
        ),
        _plot_south_asia(
            'cum_people_fully_vaccinated',
            'People Fully Vaccinated',
            lambda x, p: format(int(x), ','),
        ),
    ]
    return list(map(lambda x: x[0], plot_info_list)), \
        list(map(lambda x: x[1], plot_info_list))


def _tweet():
    status_image_files, max_country_ids = _plot_images()
    tweet_text = _get_tweet_text(max_country_ids)

    twtr = twitter.Twitter.from_args()
    twtr.tweet(
        tweet_text=tweet_text,
        status_image_files=status_image_files,
        update_user_profile=True,
    )


if __name__ == '__main__':
    _tweet()
