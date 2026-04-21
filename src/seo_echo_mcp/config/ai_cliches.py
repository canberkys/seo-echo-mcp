"""Per-language AI cliché phrases.

Community-maintained. To add a language, add its ISO 639-1 code as a key and
a list of phrases (lowercase). Match is case-insensitive substring search.
"""

from __future__ import annotations

AI_CLICHES: dict[str, list[str]] = {
    "tr": [
        "dijital çağda",
        "günümüz dünyasında",
        "günümüzde",
        "sonuç olarak",
        "özetle",
        "kapsamlı bir şekilde",
        "detaylıca inceledik",
        "derinlemesine",
        "hızla değişen dünyada",
        "teknolojinin ilerlemesiyle",
        "adeta",
        "söz konusu olduğunda",
        "ele aldık",
        "unutmayın ki",
        "şunu belirtmek gerekir ki",
    ],
    "en": [
        "in today's digital age",
        "in the modern era",
        "at the end of the day",
        "it's worth noting",
        "it goes without saying",
        "in conclusion",
        "to sum up",
        "delve into",
        "tapestry",
        "realm",
        "landscape",
        "in this comprehensive guide",
        "embark on a journey",
        "navigate the complexities",
        "unlock the potential",
        "in the fast-paced world",
    ],
    "es": [
        "en la era digital",
        "en el mundo actual",
        "en conclusión",
        "profundizar en",
        "a fin de cuentas",
        "cabe destacar",
        "sin lugar a dudas",
        "en este mundo acelerado",
    ],
    "fr": [
        "à l'ère numérique",
        "dans le monde d'aujourd'hui",
        "en conclusion",
        "il est important de noter",
        "approfondir",
        "en fin de compte",
        "il va sans dire",
    ],
    "de": [
        "im digitalen zeitalter",
        "in der heutigen welt",
        "abschließend",
        "es ist wichtig zu beachten",
        "eintauchen in",
        "in der schnelllebigen welt",
    ],
}


def cliches_for(language: str) -> list[str]:
    """Return cliché list for language, falling back to English."""
    return AI_CLICHES.get(language, AI_CLICHES["en"])
