"""Example Tweet."""
import logging
import numpy as np

from utils import timex, twitter
from covid19 import lk_data
from covid19.plots_tcr import MW, DAYS_PLOT, _plot_tcr, _plot_ctr


logging.basicConfig(level=logging.INFO)
log = logging.getLogger('covid19.twitter')


def _get_tweet_text():
    timeseries = lk_data.get_timeseries()
    latest_item = timeseries[-1]
    unixtime = latest_item['unixtime']
    date = timex.format_time(unixtime, '%Y-%m-%d')

    y = list(map(
        lambda d: d['new_pcr_tests'] / d['new_confirmed'],
        timeseries[-DAYS_PLOT-MW + 1:],
    ))
    y = np.convolve(
        y,
        np.ones(MW) / MW,
        'valid',
    )

    tcr_now = y[-1]
    tcr_mw_ago = y[-1-MW]

    tweet_text = '''Test-to-Case Ratio {date} #COVID19SL

Current: {tcr_now:.1f} Tests/Cases ({mw} Day Average)
{mw} Days Ago: {tcr_mw_ago:.1f} Tests/Cases

@HPBSriLanka @JHUSystems @OurWorldInData #lka #SriLanka
    '''.format(
        date=date,
        mw=MW,
        tcr_now=tcr_now,
        tcr_mw_ago=tcr_mw_ago,
    )
    return tweet_text


def _get_status_image_files():
    return [
        _plot_tcr(),
        _plot_ctr(),
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
