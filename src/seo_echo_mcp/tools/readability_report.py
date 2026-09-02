"""readability_report: per-language readability metrics."""

from __future__ import annotations

import logging
import math
import re

from seo_echo_mcp.schemas import ReadabilityReport
from seo_echo_mcp.utils.text import (
    count_syllables_en,
    markdown_to_plain,
    strip_frontmatter,
    tokenize_words,
)

logger = logging.getLogger(__name__)

# Average words-per-minute reading speed per language (academic references).
_WPM: dict[str, int] = {
    "en": 238,
    "tr": 180,
    "de": 179,
    "fr": 195,
    "es": 220,
    "it": 200,
    "pt": 200,
}

_PASSIVE_EN = re.compile(
    r"\b(?:am|is|are|was|were|be|been|being)\b\s+\w+(?:ed|en)\b", re.IGNORECASE
)

# Turkish passive: verb + -ıl-/-il-/-ul-/-ül- / -ın-/-in-/-un-/-ün- infixes,
# typically followed by tense markers (-dı/-di/-du/-dü/-tı/-ti etc. or -ıyor).
_PASSIVE_TR = re.compile(
    r"\b\w{3,}(?:[ıiuü]l|[ıiuü]n)(?:[dt][ıiuü]|m[ıiuü][şs]|[ıiuü]yor)\w*\b",
    re.IGNORECASE,
)

# German passive: werden-family auxiliary + past participle (ge- or -iert endings).
_PASSIVE_DE = re.compile(
    r"\b(?:wird|werden|wurde|wurden|geworden|worden)\b\s+(?:\w+\s+){0,3}\w*(?:ge\w+|\w+iert)\b",
    re.IGNORECASE,
)

# French passive: être-family auxiliary + past participle (agreeing adjective ending).
_PASSIVE_FR = re.compile(
    r"\b(?:est|sont|était|étaient|sera|seront|fut|furent)\s+\w+[eé][es]?\b",
    re.IGNORECASE,
)

# Spanish passive: ser/estar-family auxiliary + past participle (-ado/-ada/-ido/-ida).
_PASSIVE_ES = re.compile(
    r"\b(?:es|son|era|eran|fue|fueron|será|serán|sido)\s+\w+(?:ado|ada|ados|adas|ido|ida|idos|idas)\b",
    re.IGNORECASE,
)

# Italian passive: essere/venire auxiliary + past participle (-ato/-ita/-uto endings).
_PASSIVE_IT = re.compile(
    r"\b(?:è|sono|era|erano|viene|vengono|fu|furono|sarà|saranno)\s+\w+(?:ato|ata|ati|ate|ito|ita|iti|ite|uto|uta|uti|ute)\b",
    re.IGNORECASE,
)

# Portuguese passive: ser/estar auxiliary + past participle (-ado/-ada/-ido/-ida).
_PASSIVE_PT = re.compile(
    r"\b(?:é|são|era|eram|foi|foram|será|serão|sido|está|estão|estava|estavam)\s+\w+(?:ado|ada|ados|adas|ido|ida|idos|idas)\b",
    re.IGNORECASE,
)


async def readability_report(content_markdown: str, language: str = "en") -> ReadabilityReport:
    """Score readability of a markdown draft.

    Applies language-specific formulas where available:
      - `flesch-en` for English (Flesch Reading Ease)
      - `atesman-tr` for Turkish (Ateşman 1997)
      - `fernandez-huerta-es` for Spanish
      - `generic` (sentence/word complexity) for others

    Args:
        content_markdown: Full draft with optional frontmatter.
        language: ISO 639-1 code.

    Returns:
        ReadabilityReport with formula used, score, verdict, and supporting stats.
    """
    if not content_markdown or not content_markdown.strip():
        raise ValueError("`content_markdown` must be a non-empty string.")
    body = strip_frontmatter(content_markdown)
    plain = markdown_to_plain(body)
    words = tokenize_words(plain)
    sentences = [s for s in re.split(r"[.!?]+", plain) if s.strip()]

    word_count = len(words)
    sentence_count = max(len(sentences), 1)
    avg_sentence_words = word_count / sentence_count if word_count else 0.0

    syllables = sum(count_syllables_en(w) for w in words) if words else 0
    avg_syllables = syllables / word_count if word_count else 0.0

    passive_ratio: float | None = None
    passive_pattern = _PASSIVE_PATTERNS.get(language)
    if passive_pattern is not None:
        passive_hits = len(passive_pattern.findall(plain))
        passive_ratio = passive_hits / sentence_count if sentence_count else 0.0

    score, formula, verdict, grade = _score(language, avg_sentence_words, avg_syllables, words)

    wpm = _WPM.get(language, 200)
    reading_time_seconds = math.ceil(word_count / wpm * 60) if word_count else 0

    logger.info(
        "readability_report formula=%s score=%.1f verdict=%s words=%d reading_time=%ds",
        formula,
        score,
        verdict,
        word_count,
        reading_time_seconds,
    )

    return ReadabilityReport(
        language=language,
        formula_used=formula,
        score=round(score, 2),
        verdict=verdict,
        grade_level=round(grade, 2),
        word_count=word_count,
        sentence_count=sentence_count,
        avg_sentence_words=round(avg_sentence_words, 2),
        avg_syllables_per_word=round(avg_syllables, 2),
        passive_voice_ratio=round(passive_ratio, 3) if passive_ratio is not None else None,
        reading_time_seconds=reading_time_seconds,
    )


def _score(
    language: str, avg_sw: float, avg_syl: float, words: list[str]
) -> tuple[float, str, str, float]:
    if language == "en":
        score = 206.835 - 1.015 * avg_sw - 84.6 * avg_syl
        grade = 0.39 * avg_sw + 11.8 * avg_syl - 15.59
        return score, "flesch-en", _verdict_flesch(score), grade
    if language == "tr":
        # Ateşman 1997 for Turkish
        score = 198.825 - 40.175 * avg_syl - 2.610 * avg_sw
        grade = 0.39 * avg_sw + 11.8 * avg_syl - 15.59
        return score, "atesman-tr", _verdict_flesch(score), grade
    if language == "es":
        # Fernández-Huerta
        score = 206.84 - 60.0 * avg_syl - 1.02 * avg_sw
        grade = 0.39 * avg_sw + 11.8 * avg_syl - 15.59
        return score, "fernandez-huerta-es", _verdict_flesch(score), grade
    if language == "it":
        # Gulpease Index (Lucisano & Piemontese 1988)
        avg_letters = sum(len(w) for w in words) / max(len(words), 1)
        score = 89.0 - 10.0 * avg_letters + (300.0 / avg_sw if avg_sw else 0.0)
        score = max(0.0, min(100.0, score))
        grade = avg_letters * 0.6 + avg_sw * 0.2
        return score, "gulpease-it", _verdict_flesch(score), grade
    if language == "fr":
        # Kandel & Moles (1958) — French adaptation of Flesch
        score = 209.0 - 1.15 * avg_sw - 68.0 * avg_syl
        grade = 0.39 * avg_sw + 11.8 * avg_syl - 15.59
        return score, "kandel-moles-fr", _verdict_flesch(score), grade
    if language == "pt":
        # Flesch adapted for Portuguese (Martins et al. 1996)
        score = 206.835 - 1.015 * avg_sw - 84.6 * avg_syl
        grade = 0.39 * avg_sw + 11.8 * avg_syl - 15.59
        return score, "flesch-pt", _verdict_flesch(score), grade
    # Generic: penalize long sentences + long words
    long_word_ratio = sum(1 for w in words if len(w) >= 7) / max(len(words), 1)
    score = max(0.0, 100.0 - avg_sw * 2.0 - long_word_ratio * 100.0)
    grade = avg_sw * 0.4 + long_word_ratio * 10.0
    return score, "generic", _verdict_flesch(score), grade


def _verdict_flesch(score: float) -> str:
    if score >= 70:
        return "easy"
    if score >= 50:
        return "medium"
    return "hard"


_PASSIVE_PATTERNS: dict[str, re.Pattern[str]] = {
    "en": _PASSIVE_EN,
    "tr": _PASSIVE_TR,
    "de": _PASSIVE_DE,
    "fr": _PASSIVE_FR,
    "es": _PASSIVE_ES,
    "it": _PASSIVE_IT,
    "pt": _PASSIVE_PT,
}
