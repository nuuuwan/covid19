from deep_translator import GoogleTranslator
from utils import timex
from utils.cache import cache

CACHE_NAME = 'covid19.lk_vax_centers'

translator_si = GoogleTranslator(source='english', target='sinhala')


@cache(CACHE_NAME, timex.SECONDS_IN.YEAR)
def translate_si(text):
    """Translate text."""
    if len(text) <= 3:
        return text
    return translator_si.translate(text)


translator_ta = GoogleTranslator(source='english', target='tamil')


@cache(CACHE_NAME, timex.SECONDS_IN.YEAR)
def translate_ta(text):
    """Translate text."""
    if len(text) <= 3:
        return text
    return translator_ta.translate(text)
