"""Example Tweet."""
import logging

from utils import timex, twitter

from covid19 import epid, plots_vax

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
    rate_14days = (y[-1] - y[-1 - 14]) / (t[-1] - t[-1 - 14]) * Q
    rate_28days = (y[-1] - y[-1 - 28]) / (t[-1] - t[-1 - 28]) * Q
    (y[-1] - y[0]) / (t[-1] - t[0]) * Q
    cum_total = y[-1]
    cum_total_m = cum_total / 1_000_000
    goal = plots_vax.POPULATION * 4 / 3
    goal_m = goal / 1_000_000
    p_goal = cum_total_m / goal_m
    days_to_goal_28d = goal * (1 - p_goal) / rate_28days
    goal_date_28d = timex.format_time(ut + days_to_goal_28d * Q, '%B %d, %Y')

    tweet_text = '''#COVID19SL #Vaccinations 💉  {date}

{cum_total_m:,.1f}M Total Vaxs
{rate_14days:,.0f} Vax/Day (14d avg.)
{rate_28days:,.0f} Vax/Day (28d avg.)

{p_goal:.1%} of Goal*
* Vax pop > 20 years (~{goal_m:,.0f}M Vaxs)

{days_to_goal_28d:,.0f} Days ({goal_date_28d}) to Goal (at 28d rate)

@HPBSriLanka @JHUSystems @OurWorldInData #lka #SriLanka
    '''.format(
        date=date,
        rate_14days=rate_14days,
        rate_28days=rate_28days,
        cum_total_m=cum_total_m,
        goal_m=goal_m,
        p_goal=p_goal,
        days_to_goal_28d=days_to_goal_28d,
        goal_date_28d=goal_date_28d,
    )
    return tweet_text


def _get_status_image_files():
    return [
        plots_vax._plot_vax_proj(),
        plots_vax._plot_vax_summary(),
        plots_vax._plot_vax_breakdown(),
    ]


def _tweet():
    tweet_text = _get_tweet_text()
    status_image_files = _get_status_image_files()
    twtr = twitter.Twitter.from_args()
    twtr.tweet(
        tweet_text=tweet_text,
        status_image_files=status_image_files,
        profile_image_file=plots_vax._draw_profile_image_with_stat(),
        update_user_profile=True,
    )


if __name__ == '__main__':
    _tweet()
