"""Language-aware slug transliteration maps.

English/other languages fall back to Unicode NFKD + ASCII filter. Turkish,
German, Polish-style characters are handled explicitly because their NFKD
decomposition strips diacritics in ways that change meaning (e.g. "ğ" → "g"
is fine but "ı" needs to map to "i" not be dropped).
"""

from __future__ import annotations

TRANSLITERATE: dict[str, dict[str, str]] = {
    "tr": {
        "ı": "i",
        "İ": "i",
        "ş": "s",
        "Ş": "s",
        "ğ": "g",
        "Ğ": "g",
        "ü": "u",
        "Ü": "u",
        "ö": "o",
        "Ö": "o",
        "ç": "c",
        "Ç": "c",
    },
    "de": {
        "ä": "ae",
        "Ä": "ae",
        "ö": "oe",
        "Ö": "oe",
        "ü": "ue",
        "Ü": "ue",
        "ß": "ss",
    },
    "es": {
        "ñ": "n",
        "Ñ": "n",
    },
    "fr": {
        "œ": "oe",
        "Œ": "oe",
        "æ": "ae",
        "Æ": "ae",
    },
    "it": {
        "à": "a",
        "À": "a",
        "è": "e",
        "È": "e",
        "é": "e",
        "É": "e",
        "ì": "i",
        "Ì": "i",
        "î": "i",
        "Î": "i",
        "ò": "o",
        "Ò": "o",
        "ù": "u",
        "Ù": "u",
    },
    "pt": {
        "ã": "a",
        "Ã": "a",
        "â": "a",
        "Â": "a",
        "á": "a",
        "Á": "a",
        "à": "a",
        "À": "a",
        "ç": "c",
        "Ç": "c",
        "ê": "e",
        "Ê": "e",
        "é": "e",
        "É": "e",
        "í": "i",
        "Í": "i",
        "õ": "o",
        "Õ": "o",
        "ô": "o",
        "Ô": "o",
        "ó": "o",
        "Ó": "o",
        "ú": "u",
        "Ú": "u",
    },
}

# Small connector words to optionally drop from slugs to keep them short.
STOPWORDS: dict[str, set[str]] = {
    "en": {"a", "an", "the", "of", "and", "or", "for", "to", "in", "on", "with"},
    "tr": {"ve", "ile", "bir", "bu", "şu", "için", "ya", "veya"},
    "es": {"el", "la", "los", "las", "de", "del", "y", "o", "un", "una", "en"},
    "fr": {"le", "la", "les", "de", "du", "des", "et", "ou", "un", "une", "en", "dans"},
    "de": {"der", "die", "das", "und", "oder", "ein", "eine", "mit", "zu"},
    "it": {"il", "lo", "la", "le", "gli", "un", "una", "di", "da", "in", "con", "su", "per", "tra", "fra", "e", "o"},
    "pt": {"o", "a", "os", "as", "um", "uma", "de", "da", "do", "das", "dos", "em", "na", "no", "nas", "nos", "com", "por", "para", "e", "ou", "se"},
}
