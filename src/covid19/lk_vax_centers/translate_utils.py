from deep_translator import GoogleTranslator
from utils.cache import cache

from covid19.lk_vax_centers.lk_vax_center_constants import (CACHE_DIR,
                                                            CACHE_NAME,
                                                            CACHE_TIMEOUT)

translator_si = GoogleTranslator(source='english', target='sinhala')


@cache(CACHE_NAME, CACHE_TIMEOUT, CACHE_DIR)
def translate_si(text):
    """Translate text."""
    if len(text) <= 3:
        return text
    return translator_si.translate(text)


translator_ta = GoogleTranslator(source='english', target='tamil')


@cache(CACHE_NAME, CACHE_TIMEOUT, CACHE_DIR)
def translate_ta(text):
    """Translate text."""
    if len(text) <= 3:
        return text
    return translator_ta.translate(text)
