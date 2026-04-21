"""Language-aware slug transliteration maps.

English/other languages fall back to Unicode NFKD + ASCII filter. Turkish,
German, Polish-style characters are handled explicitly because their NFKD
decomposition strips diacritics in ways that change meaning (e.g. "ğ" → "g"
is fine but "ı" needs to map to "i" not be dropped).
"""

from __future__ import annotations

TRANSLITERATE: dict[str, dict[str, str]] = {
    "tr": {
        "ı": "i", "İ": "i",
        "ş": "s", "Ş": "s",
        "ğ": "g", "Ğ": "g",
        "ü": "u", "Ü": "u",
        "ö": "o", "Ö": "o",
        "ç": "c", "Ç": "c",
    },
    "de": {
        "ä": "ae", "Ä": "ae",
        "ö": "oe", "Ö": "oe",
        "ü": "ue", "Ü": "ue",
        "ß": "ss",
    },
    "es": {
        "ñ": "n", "Ñ": "n",
    },
    "fr": {
        "œ": "oe", "Œ": "oe",
        "æ": "ae", "Æ": "ae",
    },
}

# Small connector words to optionally drop from slugs to keep them short.
STOPWORDS: dict[str, set[str]] = {
    "en": {"a", "an", "the", "of", "and", "or", "for", "to", "in", "on", "with"},
    "tr": {"ve", "ile", "bir", "bu", "şu", "için", "ya", "veya"},
    "es": {"el", "la", "los", "las", "de", "del", "y", "o", "un", "una", "en"},
    "fr": {"le", "la", "les", "de", "du", "des", "et", "ou", "un", "une", "en", "dans"},
    "de": {"der", "die", "das", "und", "oder", "ein", "eine", "mit", "zu"},
}
