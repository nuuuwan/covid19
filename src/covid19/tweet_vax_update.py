"""Example Tweet."""
import logging

from utils import timex, twitter

from covid19 import (PlotVaxBreakdown, PlotVaxBreakdownDaily,
                     PlotVaxProfileImage, PlotVaxProjection, PlotVaxSummary,
                     epid)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('covid19.twitter')


def _get_tweet_text():
    timeseries = epid.load_timeseries()
    latest_item = timeseries[-1]
    ut = latest_item['ut']
    date = timex.format_time(ut, '%Y-%m-%d')

    t = list(
        map(
            lambda d: d['ut'],
            timeseries,
        )
    )
    y = list(
        map(
            lambda d: d['cum_total'],
            timeseries,
        )
    )
    y[-1]
    Q = timex.SECONDS_IN.DAY
    most_recent = y[-1] - y[-2]
    rate_7days = (y[-1] - y[-1 - 7]) / (t[-1] - t[-1 - 7]) * Q
    rate_28days = (y[-1] - y[-1 - 28]) / (t[-1] - t[-1 - 28]) * Q
    (y[-1] - y[0]) / (t[-1] - t[0]) * Q
    cum_total = y[-1]
    cum_total_m = cum_total / 1_000_000
    goal = PlotVaxSummary.POPULATION * 4 / 3
    goal_m = goal / 1_000_000
    p_goal = cum_total_m / goal_m
    days_to_goal_28d = goal * (1 - p_goal) / rate_28days
    goal_date_28d = timex.format_time(ut + days_to_goal_28d * Q, '%Y-%m-%d')

    tweet_text = '''#COVID19SL #Vaccinations 💉  {date}

{most_recent:,.0f}K Vaxs (latest)
{rate_7days:,.0f}K Vax/Day (7-day)
{rate_28days:,.0f}K Vax/Day (28-day)

{cum_total_m:,.1f}M Total Vaxs
{p_goal:.1%} of Goal (Vax pop > 20 years)

{days_to_goal_28d:,.0f} Days ({goal_date_28d}) to Goal (at 28-day rate)

www.epid.gov.lk #lka #SriLanka
    '''.format(
        date=date,
        most_recent=most_recent / 1000,
        rate_7days=rate_7days / 1000,
        rate_28days=rate_28days / 1000,
        cum_total_m=cum_total_m,
        p_goal=p_goal,
        days_to_goal_28d=days_to_goal_28d,
        goal_date_28d=goal_date_28d,
    )
    return tweet_text


def _get_status_image_files():
    return [
        PlotVaxProjection._plot(),
        PlotVaxSummary._plot(),
        PlotVaxBreakdown._plot(),
        PlotVaxBreakdownDaily._plot(),
    ]


def _tweet():
    tweet_text = _get_tweet_text()
    status_image_files = _get_status_image_files()
    twtr = twitter.Twitter.from_args()
    twtr.tweet(
        tweet_text=tweet_text,
        status_image_files=status_image_files,
        profile_image_file=PlotVaxProfileImage._draw(),
        banner_image_file=PlotVaxProjection._plot(is_banner_image=True),
        update_user_profile=True,
    )


if __name__ == '__main__':
    _tweet()
