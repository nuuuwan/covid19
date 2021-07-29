"""Example Tweet."""
import logging

import flag
from utils import twitter

from covid19 import covid_data

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('covid19.twitter')
MIN_POPULATION = 100_000
Q_PEOPLE = 100
MW = 7


def get_place_emoji(i):
    if i == 0:
        return '🥇'
    if i == 1:
        return '🥈'
    if i == 2:
        return '🥉'
    return '  '


def _get_tweet_text():

    jhu_data = covid_data.load_jhu_data()
    top_vax_info_list = []
    for country_alpha_2, country_data in jhu_data.items():
        if not country_data:
            continue
        population = country_data.get('population')
        if not population or population < MIN_POPULATION:
            continue
        vaxs = list(
            map(
                lambda d: (int)(d.get('new_vaccinations', 0)),
                country_data['timeseries'][-MW:],
            )
        )
        vaxs_mw = Q_PEOPLE * sum(vaxs) / population

        country_name = country_data['country_name']
        top_vax_info_list.append(
            dict(
                country_alpha_2=country_alpha_2,
                country_name=country_name,
                vaxs_mw=vaxs_mw,
            )
        )

    top_vax_info_list = sorted(
        top_vax_info_list,
        key=lambda top_vax_info: -top_vax_info['vaxs_mw'],
    )

    inner_lines = []
    for i, top_vax_info in enumerate(top_vax_info_list[:10]):
        if i == 3:
            inner_lines.append('')
        inner_lines.append(
            '{place} {vaxs_mw:.1f} {flag}  #{country_name}'.format(
                place=get_place_emoji(i),
                flag=flag.flag(top_vax_info['country_alpha_2']),
                country_name=top_vax_info['country_name'].replace(' ', ''),
                vaxs_mw=top_vax_info['vaxs_mw'],
            )
        )
        inner = '\n'.join(inner_lines)
        if len(inner) > 180:
            break

    tweet_text = '''#COVID19 Vaxs/{Q_PEOPLE:.0f} Ppl. — Last {MW} Days

{inner}

(pop > {MIN_POPULATION_K:.0f}K)

@OurWorldInData #lka #COVID19SL
    '''.format(
        inner=inner,
        MW=MW,
        Q_PEOPLE=Q_PEOPLE,
        MIN_POPULATION_K=MIN_POPULATION / 1_000.0,
    )
    return tweet_text


def _tweet():
    tweet_text = _get_tweet_text()
    twtr = twitter.Twitter.from_args()

    twtr.tweet(
        tweet_text=tweet_text,
        update_user_profile=True,
    )


if __name__ == '__main__':
    _tweet()
