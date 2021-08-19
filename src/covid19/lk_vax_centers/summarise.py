from utils import filex, timex, tsv
import os

from covid19._utils import log
from covid19.lk_vax_centers import lk_vax_center_utils
from covid19.lk_vax_centers.lk_vax_center_constants import VAX_DASH_URL


def dump_summary(date_id, lang):
    date = timex.format_time(timex.get_unixtime(), '%Y-%m-%d')
    tsv_file = lk_vax_center_utils.get_file(date_id, 'tsv')
    if not os.path.exists(tsv_file):
        log.error(f'{tsv_file} does not exist. Aborting.')
        return False

    data_list = tsv.read(tsv_file)

    if lang == 'si':
        title = 'කොවිඩ්19 එන්නත් මධ්‍යස්ථාන'
        warning = (
            'ස්ථාන පදනම් වී ඇත්තේ ස්වයංක්‍රීය ගූගල් සිතියම් (Google Maps) '
            + 'සෙවීම මත වන අතර ඒවා නිවැරදි නොවිය හැකිය.'
        )
        source_str = 'මූලාශ්‍ර වෙබ් අඩවිය'
    elif lang == 'ta':
        title = 'கோவிட்19 தடுப்பூசி மையங்கள்'
        warning = (
            'இருப்பிடங்கள் தானியங்கி கூகுள் மேப்ஸ் தேடலை (Google Maps) '
            + 'அடிப்படையாகக் கொண்டவை மற்றும் துல்லியமாக இருக்காது.'
        )
        source_str = 'மூல வலைத்தளம்'
    else:
        title = 'COVID19 Vaccinations Centers'
        warning = (
            'Locations are based on Automated GoogleMaps Search, '
            + 'and might be inaccurate.'
        )
        source_str = 'Source Website'

    md_lines = [
        f'# {title} ({date})',
        '',
        f'{source_str}: [{VAX_DASH_URL}]({VAX_DASH_URL})',
        '',
        f'*{warning}*',
        '',
        '-----',
    ]
    prev_district, prev_police = None, None
    for data in data_list:
        if lang == 'si':
            district = data['district_si']
            police = data['police_si']
            center = data['center_si']
            formatted_address = data['formatted_address_si']
            police_area_str = 'පොලිස් බල ප්‍රදේශය'
            district_str = 'දිස්ත්‍රික්කය'
            dose_str = 'මාත්‍රාව'
            str_1st = '1වන'
            str_2nd = '2වන'

        elif lang == 'ta':
            district = data['district_ta']
            police = data['police_ta']
            center = data['center_ta']
            formatted_address = data['formatted_address_ta']
            police_area_str = 'போலீஸ் பகுதி'
            district_str = 'மாவட்டம்'
            dose_str = 'டோஸ்'
            str_1st = '1வது'
            str_2nd = '2வது'

        else:
            district = data['district']
            police = data['police']
            center = data['center']
            formatted_address = data['formatted_address']
            police_area_str = 'Police Area'
            district_str = 'District'
            dose_str = 'Dose'
            str_1st = '1st'
            str_2nd = '2nd'

        dose_tokens = []
        if data['dose1'] == 'True':
            dose_tokens.append(f'{str_1st} {dose_str}')
        if data['dose2'] == 'True':
            dose_tokens.append(f'{str_2nd} {dose_str}')
        dose = ', '.join(dose_tokens)
        if dose:
            dose = f' ({dose}) '

        if formatted_address:
            lat = data['lat']
            lng = data['lng']
            link = f'https://www.google.lk/maps/place/{lat}N,{lng}E'
            md_link = f'[{formatted_address}]({link})'
        else:
            md_link = '(Location Unknown)'

        if district != prev_district:
            md_lines.append(f'## {district} {district_str}')
        if police != prev_police:
            md_lines.append(f'* **{police}** {police_area_str}')
        md_lines.append(f'  * {dose}{center} - {md_link} ')

        prev_district, prev_police = district, police

    md_file = lk_vax_center_utils.get_file(date_id, f'{lang}.md')
    md = '\n'.join(md_lines)
    filex.write(md_file, md)
    log.info(f'Wrote summary to {md_file}')


if __name__ == '__main__':
    date_id = timex.get_date_id()
    dump_summary(date_id, 'en')
    dump_summary(date_id, 'si')
    dump_summary(date_id, 'ta')
