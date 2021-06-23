"""Example Tweet."""
import datetime
import tweepy
import argparse
import logging
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np

from utils import timex
from covid19 import lk_data, covid_data
from covid19.plots import _plot_south_asia


logging.basicConfig(level=logging.INFO)
log = logging.getLogger('covid19.twitter')


def _get_country_label(country_id):
    if country_id == 'LK':
        return '🇱🇰  #SriLanka'
    if country_id == 'IN':
        return '🇮🇳  #India'
    if country_id == 'PK':
        return '🇵🇰  #Pakistan'
    if country_id == 'NP':
        return '🇳🇵  #Nepal'
    if country_id == 'BD':
        return '🇧🇩  #Bangladesh'
    if country_id == 'AF':
        return '🇦🇫  #Afghanistan'
    if country_id == 'MV':
        return '🇲🇻  #Maldives'
    if country_id == 'BT':
        return '🇧🇹  #Bhutan'


def _get_tweet_text(max_country_ids):
    jhu_data = covid_data.load_jhu_data()
    _ds = jhu_data['LK']['timeseries'][-1]['date'][:10]
    print(max_country_ids)

    return '''
#COVID19 #SouthAsia ({_ds})

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
        list(map(lambda x: x[1], plot_info_list)),


def _tweet(
    twtr_api_key,
    twtr_api_secret_key,
    twtr_access_token,
    twtr_access_token_secret,
):
    image_files, max_country_ids = _plot_images()
    log.info('Status images: %s', ';'.join(image_files))

    tweet_text = _get_tweet_text(max_country_ids)
    log.info('Tweeting: %s', tweet_text)
    log.info('Tweet Length: %d', len(tweet_text))


    if not twtr_api_key:
        return

    auth = tweepy.OAuthHandler(twtr_api_key, twtr_api_secret_key)
    auth.set_access_token(twtr_access_token, twtr_access_token_secret)
    api = tweepy.API(auth)

    media_ids = []
    for image_file in image_files:
        res = api.media_upload(image_file)
        media_id = res.media_id
        media_ids.append(media_id)
        log.info('Uploaded image %s to twitter as %s', image_file, media_id)

    log.info(api.update_status(tweet_text, media_ids=media_ids))

    date = timex.format_time(timex.get_unixtime(), '%B %d, %Y %H:%M%p')
    timezone = timex.get_timezone()
    log.info(api.update_profile(
        description='''Statistics about Sri Lanka.

Automatically updated at {date} {timezone}
        '''.format(date=date, timezone=timezone)
    ))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Tweet South Asia Update.',
    )
    for twtr_arg_name in [
        'twtr_api_key',
        'twtr_api_secret_key',
        'twtr_access_token',
        'twtr_access_token_secret',
    ]:
        parser.add_argument(
            '--' + twtr_arg_name,
            type=str,
            required=False,
            default=None,
        )
    args = parser.parse_args()
    _tweet(
        args.twtr_api_key,
        args.twtr_api_secret_key,
        args.twtr_access_token,
        args.twtr_access_token_secret,
    )
