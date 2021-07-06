"""Example Tweet."""
import logging

from utils import timex, twitter
from covid19 import lk_data
from covid19.plots_lk import \
    MW, POPULATION, \
    _plot_simple, _plot_with_time_window, _draw_profile_image_with_stat


logging.basicConfig(level=logging.INFO)
log = logging.getLogger('covid19.twitter')


def _get_tweet_text():
    timeseries = lk_data.get_timeseries()
    latest_item = timeseries[-1]
    unixtime = latest_item['unixtime']
    date = timex.format_time(unixtime, '%Y-%m-%d')

    ts_active = list(map(lambda _i: _i['active'], timeseries))
    ts_new_deaths = list(map(lambda _i: _i['new_deaths'], timeseries))
    ts_new_pcr_tests = list(map(lambda _i: _i['new_pcr_tests'], timeseries))

    ts_cum_vaxs = \
        list(map(lambda _i: _i['cum_vaxs'], timeseries))
    ts_cum_people_vaccinated = \
        list(map(lambda _i: _i['cum_people_vaccinated'], timeseries))
    ts_cum_people_fully_vaccinated = \
        list(map(lambda _i: _i['cum_people_fully_vaccinated'], timeseries))

    active = ts_active[-1]
    active_wa = ts_active[-8]
    delta_active = active - active_wa
    active_arrow = '🔴' if (delta_active > 0) else '🟢'

    new_deaths_rwday = sum(ts_new_deaths[-MW:]) / MW
    new_deaths_rwday_wa = \
        sum(ts_new_deaths[-MW-MW:-MW]) / MW
    delta_new_deaths = new_deaths_rwday - new_deaths_rwday_wa
    new_deaths_rwday_arrow = '🔴' if (delta_new_deaths > 0) else '🟢'

    new_vacci_rwday = (ts_cum_vaxs[-1] - ts_cum_vaxs[-MW-1]) / MW
    new_vacci_rwday_wa = (ts_cum_vaxs[-1-MW] - ts_cum_vaxs[-MW-1-MW]) / MW
    delta_new_vacci = new_vacci_rwday - new_vacci_rwday_wa
    new_vacci_rwday_arrow = '🟢' if (delta_new_vacci > 0) else '🔴'

    vacci_dose_1 = ts_cum_people_vaccinated[-1]
    vacci_dose_2 = ts_cum_people_fully_vaccinated[-1]
    p_vacci_dose_1 = vacci_dose_1 / POPULATION
    p_vacci_dose_2 = vacci_dose_2 / POPULATION

    new_pcr_tests_rwday = sum(ts_new_pcr_tests[-MW:]) / MW
    new_pcr_tests_rwday_wa = sum(ts_new_pcr_tests[-MW-MW:-MW]) / MW
    delta_new_pcr_tests = new_pcr_tests_rwday - new_pcr_tests_rwday_wa
    new_pcr_tests_rwday_arrow = '🟢' if (delta_new_pcr_tests > 0) else '🔴'

    tweet_text = '''{date} #COVID19SL

{active_arrow} Active:
    {active:,} ({delta_active:+,} {MW}days ago)
{new_deaths_rwday_arrow} Deaths/day﹘{MW}day avg:
    {new_deaths_rwday:,.0f} ({delta_new_deaths:+,.0f})
{new_pcr_tests_rwday_arrow} Tests/day﹘{MW}day avg:
    {new_pcr_tests_rwday:,.0f} ({delta_new_pcr_tests:+,.0f})
{new_vacci_rwday_arrow} Vaxs/Day﹘{MW}day avg:
    {new_vacci_rwday:,.0f} ({delta_new_vacci:+,.0f})

- Pop vaxed: {p_vacci_dose_1:.1%}
- Pop fully vaxed: {p_vacci_dose_2:.1%}

@HPBSriLanka @JHUSystems @OurWorldInData #lka #SriLanka
    '''.format(
        MW=MW,
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


def _get_status_image_files():
    return [
        _plot_simple('active', 'blue', 'Active COVID19 Cases'),
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
            'new_vaxs',
            'green',
            'lightgreen',
            'Daily COVID19 Vaccinations',
        ),
    ]


def _tweet():
    tweet_text = _get_tweet_text()
    status_image_files = _get_status_image_files()
    profile_image_file = _draw_profile_image_with_stat()
    banner_image_file = _plot_with_time_window(
        'new_vaxs',
        'green',
        'lightgreen',
        'Daily COVID19 Vaccinations',
        is_background_image=True,
    )

    twtr = twitter.Twitter.from_args()
    twtr.tweet(
        tweet_text=tweet_text,
        status_image_files=status_image_files,
        update_user_profile=True,
        profile_image_file=profile_image_file,
        banner_image_file=banner_image_file,
    )


if __name__ == '__main__':
    _tweet()
