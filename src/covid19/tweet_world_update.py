"""Example Tweet."""
import logging

from utils import twitter

from covid19 import PlotWorld

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('covid19.twitter')


def _place_name_to_label(place_name):
    return {
        'Sri Lanka': '🇱🇰#SriLanka',
        'India': '🇮🇳#India',
        'China': '🇨🇳#China',
        'USA': '🇺🇸#USA',
        'Europe': '🇪🇺#Europe',
        'Africa': '🌍#Africa',
        'South America': '🌎#SouthAmerica',
        'North America (Rest of)': '🌎#NorthAmerica (Rest)',
        'Asia (Rest of)': '🌏#Asia (Rest)',
        'Oceania': '🌏#Oceania',
        'World': '🌏#World (All)',
    }.get(place_name, place_name)


def _get_tweet_text(group_to_y):

    inner_lines = []
    for group_id, y in group_to_y.items():
        place_name = PlotWorld._place_id_to_name(group_id)
        label = _place_name_to_label(place_name)
        stat = y[-1]
        inner_lines.append(
            '{stat:.0f} {label}'.format(
                stat=stat,
                label=label,
            )
        )
        if group_id == 'World':
            inner_lines.append('')
    inner = '\n'.join(inner_lines)

    tweet_text = '''#COVID19SL vs. World

{MW}-Day Avg Vax/{Q_PEOPLE_K:.0f}K people

{inner}

@JHUSystems @OurWorldInData#lka
    '''.format(
        inner=inner,
        MW=PlotWorld.MW,
        Q_PEOPLE_K=PlotWorld.Q_PEOPLE / 1_000,
    )
    return tweet_text


def _get_status_image_files():
    image_files = []
    for (field_key, label) in [
        ('cum_vaccinations', 'Total Vaccinations'),
        ('cum_people_fully_vaccinated', 'Fully Vaccinated People'),
        ('cum_people_vaccinated', 'Vaccinated People (at least 1 dose)'),
        (
            'new_vaccinations',
            'New Vaccinations (%d-Day Average)' % (PlotWorld.MW),
        ),
    ]:
        image_file, group_to_y = PlotWorld._plot(field_key, label)
        image_files.append(image_file)
    return image_files, group_to_y


def _tweet():
    status_image_files, group_to_y = _get_status_image_files()
    tweet_text = _get_tweet_text(group_to_y)
    twtr = twitter.Twitter.from_args()
    print(len(tweet_text))

    twtr.tweet(
        tweet_text=tweet_text,
        status_image_files=status_image_files,
        update_user_profile=True,
    )


if __name__ == '__main__':
    _tweet()
