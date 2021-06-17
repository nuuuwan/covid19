"""Example Tweet."""
import datetime
import tweepy
import argparse
import logging
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np

from utils import timex
from covid19 import lk_data
from covid19.plots import _plot_simple, _plot_with_time_window

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('covid19.twitter')


def _get_tweet_text():
    ROLLING_WINDOW = 14
    timeseries = lk_data.get_timeseries()
    latest_item = timeseries[-1]
    unixtime = latest_item['unixtime']
    date = timex.format_time(unixtime, '%Y-%m-%d')

    ts_active = list(map(lambda _i: _i['active'], timeseries))

    ts_new_deaths = list(map(lambda _i: _i['new_deaths'], timeseries))

    ts_new_pcr_tests = list(map(lambda _i: _i['new_pcr_tests'], timeseries))

    ts_cum_vaccinations = \
        list(map(lambda _i: _i['cum_vaccinations'], timeseries))
    ts_cum_people_vaccinated = \
        list(map(lambda _i: _i['cum_people_vaccinated'], timeseries))
    ts_cum_people_fully_vaccinated = \
        list(map(lambda _i: _i['cum_people_fully_vaccinated'], timeseries))

    active = ts_active[-1]
    active_wa = ts_active[-8]
    delta_active = active - active_wa
    active_arrow = '🔴' if (delta_active > 0) else '🟢'

    new_deaths_rwday = sum(ts_new_deaths[-ROLLING_WINDOW:]) / ROLLING_WINDOW
    new_deaths_rwday_wa = \
        sum(ts_new_deaths[-ROLLING_WINDOW-7:-7]) / ROLLING_WINDOW
    delta_new_deaths = new_deaths_rwday - new_deaths_rwday_wa
    new_deaths_rwday_arrow = '🔴' if (delta_new_deaths > 0) else '🟢'

    new_vacci_rwday = (ts_cum_vaccinations[-1] - ts_cum_vaccinations[-ROLLING_WINDOW-1]) / ROLLING_WINDOW
    new_vacci_rwday_wa = (ts_cum_vaccinations[-1-7] - ts_cum_vaccinations[-ROLLING_WINDOW-1-7]) / ROLLING_WINDOW
    delta_new_vacci = new_vacci_rwday - new_vacci_rwday_wa
    new_vacci_rwday_arrow = '🟢' if (delta_new_vacci > 0) else '🔴'

    POPULATION = 21_800_000
    vacci_dose_1 = ts_cum_people_vaccinated[-1]
    vacci_dose_2 = ts_cum_people_fully_vaccinated[-1]
    p_vacci_dose_1 = vacci_dose_1 / POPULATION
    p_vacci_dose_2 = vacci_dose_2 / POPULATION

    new_pcr_tests_rwday = sum(ts_new_pcr_tests[-ROLLING_WINDOW:]) / ROLLING_WINDOW
    new_pcr_tests_rwday_wa = sum(ts_new_pcr_tests[-ROLLING_WINDOW-7:-7]) / ROLLING_WINDOW
    delta_new_pcr_tests = new_pcr_tests_rwday - new_pcr_tests_rwday_wa
    new_pcr_tests_rwday_arrow = '🟢' if (delta_new_pcr_tests > 0) else '🔴'


    tweet_text = '''{date} #COVID19SL

{active_arrow} Active: {active:,} ({delta_active:+,} week ago)
{new_deaths_rwday_arrow} Deaths/day﹘{ROLLING_WINDOW}day avg: {new_deaths_rwday:,.0f} ({delta_new_deaths:+,.0f})
{new_pcr_tests_rwday_arrow} Tests/day﹘{ROLLING_WINDOW}day avg: {new_pcr_tests_rwday:,.0f} ({delta_new_pcr_tests:+,.0f})
{new_vacci_rwday_arrow} Vaxs/Day﹘{ROLLING_WINDOW}day avg: {new_vacci_rwday:,.0f} ({delta_new_vacci:+,.0f})
- Pop vaxed: {p_vacci_dose_1:.1%}
- Pop fully vaxed: {p_vacci_dose_2:.1%}

@HPBSriLanka @JHUSystems @OurWorldInData #lka #SriLanka
    '''.format(
        ROLLING_WINDOW=ROLLING_WINDOW,
        active=active,
        active_arrow=active_arrow,
        new_vacci_rwday=new_vacci_rwday,
        date=date,
        delta_new_vacci=delta_new_vacci,
        delta_active=delta_active,
        delta_new_deaths=delta_new_deaths,
        new_deaths_rwday=new_deaths_rwday,
        new_deaths_rwday_arrow=new_deaths_rwday_arrow,
        new_vacci_rwday_arrow=new_vacci_rwday_arrow,
        p_vacci_dose_1=p_vacci_dose_1,
        p_vacci_dose_2=p_vacci_dose_2,
        new_pcr_tests_rwday_arrow=new_pcr_tests_rwday_arrow,
        new_pcr_tests_rwday=new_pcr_tests_rwday,
        delta_new_pcr_tests=delta_new_pcr_tests,
    )
    return tweet_text


def _plot_charts():
    return [
        _plot_simple('active', 'blue', 'Active COVID19 Cases'),
        _plot_with_time_window('new_deaths', 'red', 'pink', 'Daily COVID19 Deaths'),
        _plot_with_time_window('new_pcr_tests', 'orange', (1, 0.9, 0.8), 'Daily COVID19 PCR Tests'),
        _plot_with_time_window('new_vaccinations', 'green', 'lightgreen', 'Daily COVID19 Vaccinations'),
    ]


def _tweet(
    twtr_api_key,
    twtr_api_secret_key,
    twtr_access_token,
    twtr_access_token_secret,
):
    tweet_text = _get_tweet_text()
    log.info('Tweeting: %s', tweet_text)
    log.info('Tweet Length: %d', len(tweet_text))
    image_files = _plot_charts()
    log.info('Media: %s', ';'.join(image_files))

    auth = tweepy.OAuthHandler(twtr_api_key, twtr_api_secret_key)
    auth.set_access_token(twtr_access_token, twtr_access_token_secret)
    api = tweepy.API(auth)

    media_ids = []
    for image_file in image_files:
        res = api.media_upload(image_file)
        media_id = res.media_id
        media_ids.append(media_id)
        log.info('Uploaded image %s to twitter as %s', image_file, media_id)

    api.update_status(tweet_text, media_ids=media_ids)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run pipeline for custom_dgigovlk_covid19.',
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
