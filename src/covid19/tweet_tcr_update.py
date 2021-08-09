"""Example Tweet."""
import logging

import numpy as np
from utils import timex, twitter

from covid19 import PlotTCRAndCTR, lk_data

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('covid19.twitter')


def _get_tweet_text():
    timeseries = lk_data.get_timeseries()
    latest_item = timeseries[-1]
    unixtime = latest_item['unixtime']
    date = timex.format_time(unixtime, '%Y-%m-%d')

    y = list(
        map(
            lambda d: d['new_pcr_tests'] / d['new_confirmed'],
            timeseries[-PlotTCRAndCTR.DAYS_PLOT - PlotTCRAndCTR.MW + 1 :],
        )
    )
    y = np.convolve(
        y,
        np.ones(PlotTCRAndCTR.MW) / PlotTCRAndCTR.MW,
        'valid',
    )

    tcr_now = y[-1]
    tcr_mw_ago = y[-1 - PlotTCRAndCTR.MW]

    tweet_text = '''Test-to-Case Ratio {date} #COVID19SL

Current: {tcr_now:.1f} Tests/Cases ({mw} Day Average)
{mw} Days Ago: {tcr_mw_ago:.1f} Tests/Cases

@HPBSriLanka @JHUSystems @OurWorldInData #lka #SriLanka
    '''.format(
        date=date,
        mw=PlotTCRAndCTR.MW,
        tcr_now=tcr_now,
        tcr_mw_ago=tcr_mw_ago,
    )
    return tweet_text


def _get_status_image_files():
    return [
        PlotTCRAndCTR._plot(),
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
