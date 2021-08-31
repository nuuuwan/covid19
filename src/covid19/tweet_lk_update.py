"""Example Tweet."""
import logging

from utils import timex, twitter

from covid19 import lk_data
from covid19.plots_lk import (
    MW,
    POPULATION,
    _plot_simple,
    _plot_with_time_window,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('covid19.twitter')


def _get_tweet_text():
    timeseries = lk_data.get_timeseries()
    latest_item = timeseries[-1]
    unixtime = latest_item['unixtime']
    date = timex.format_time(unixtime, '%Y-%m-%d')

    ts_new_confirmed = list(map(lambda _i: _i['new_confirmed'], timeseries))
    ts_new_deaths = list(map(lambda _i: _i['new_deaths'], timeseries))
    ts_new_pcr_tests = list(map(lambda _i: _i['new_pcr_tests'], timeseries))

    ts_cum_vaxs = list(map(lambda _i: _i['cum_vaccinations'], timeseries))
    ts_cum_people_vaccinated = list(
        map(lambda _i: _i['cum_people_vaccinated'], timeseries)
    )
    ts_cum_people_fully_vaccinated = list(
        map(lambda _i: _i['cum_people_fully_vaccinated'], timeseries)
    )

    new_confirmed = ts_new_confirmed[-1]
    new_confirmed_wa = ts_new_confirmed[-8]
    d_new_confirmed = new_confirmed - new_confirmed_wa
    new_confirmed_arrow = '🔴' if (d_new_confirmed > 0) else '🟢'

    new_deaths_rw = sum(ts_new_deaths[-MW:]) / MW
    new_deaths_rw_wa = sum(ts_new_deaths[-MW - MW: -MW]) / MW
    d_new_deaths = new_deaths_rw - new_deaths_rw_wa
    new_deaths_ar = '🔴' if (d_new_deaths > 0) else '🟢'

    new_vax_rw = (ts_cum_vaxs[-1] - ts_cum_vaxs[-MW - 1]) / MW
    new_vax_rw_wa = (ts_cum_vaxs[-1 - MW] - ts_cum_vaxs[-MW - 1 - MW]) / MW
    d_new_vacci = new_vax_rw - new_vax_rw_wa
    new_vax_ar = '🟢' if (d_new_vacci > 0) else '🔴'

    vax_dose_1 = ts_cum_people_vaccinated[-1]
    vax_dose_2 = ts_cum_people_fully_vaccinated[-1]
    p_vax_dose_1 = vax_dose_1 / POPULATION
    p_vax_dose_2 = vax_dose_2 / POPULATION

    new_pcr_tests_rw = sum(ts_new_pcr_tests[-MW:]) / MW
    new_pcr_tests_rw_wa = sum(ts_new_pcr_tests[-MW - MW: -MW]) / MW
    d_new_pcr_tests = new_pcr_tests_rw - new_pcr_tests_rw_wa
    new_pcr_tests_ar = '🟢' if (d_new_pcr_tests > 0) else '🔴'

    tweet_text = '''{date} #COVID19SL

{new_confirmed_arrow} Confirmed: {new_confirmed:,} ({d_new_confirmed:+,} {MW}days ago)
{new_deaths_ar} Deaths/day: {new_deaths_rw:,.0f} ({d_new_deaths:+,.0f})
{new_pcr_tests_ar} Tests/day: {new_pcr_tests_rw:,.0f} ({d_new_pcr_tests:+,.0f})
{new_vax_ar} Vaxs/Day: {new_vax_rw:,.0f} ({d_new_vacci:+,.0f})

({MW}day avg.)

- Pop vaxed: {p_vax_dose_1:.1%}
- Pop fully vaxed: {p_vax_dose_2:.1%}

@HPBSriLanka @JHUSystems @OurWorldInData #lka #SriLanka
    '''.format(
        MW=MW,
        new_confirmed=new_confirmed,
        new_confirmed_arrow=new_confirmed_arrow,
        new_vax_rw=new_vax_rw,
        date=date,
        d_new_vacci=d_new_vacci,
        d_new_confirmed=d_new_confirmed,
        d_new_deaths=d_new_deaths,
        new_deaths_rw=new_deaths_rw,
        new_deaths_ar=new_deaths_ar,
        new_vax_ar=new_vax_ar,
        p_vax_dose_1=p_vax_dose_1,
        p_vax_dose_2=p_vax_dose_2,
        new_pcr_tests_ar=new_pcr_tests_ar,
        new_pcr_tests_rw=new_pcr_tests_rw,
        d_new_pcr_tests=d_new_pcr_tests,
    )
    return tweet_text


def _get_status_image_files():
    return [
        _plot_simple('new_confirmed', 'blue', 'New Confirmed COVID19 Cases'),
        _plot_with_time_window(
            'new_deaths',
            'red',
            'pink',
            'Daily COVID19 Deaths',
        ),
        _plot_with_time_window(
            'new_pcr_tests',
            'orange',
            (1, 0.9, 0.8),
            'Daily COVID19 PCR Tests',
        ),
        _plot_with_time_window(
            'new_vaccinations',
            'green',
            'lightgreen',
            'Daily COVID19 Vaccinations',
        ),
    ]


def _tweet():
    tweet_text = _get_tweet_text()
    status_image_files = _get_status_image_files()
    twtr = twitter.Twitter.from_args()
    twtr.tweet(
        tweet_text=tweet_text,
        status_image_files=status_image_files,
        update_user_profile=True,
    )


if __name__ == '__main__':
    _tweet()
