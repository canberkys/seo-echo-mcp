"""readability_report: per-language readability metrics."""

from __future__ import annotations

import re

from seo_echo_mcp.schemas import ReadabilityReport
from seo_echo_mcp.utils.text import (
    count_syllables_en,
    markdown_to_plain,
    strip_frontmatter,
    tokenize_words,
)

_PASSIVE_EN = re.compile(
    r"\b(?:am|is|are|was|were|be|been|being)\b\s+\w+(?:ed|en)\b", re.IGNORECASE
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
    if language == "en":
        passive_hits = len(_PASSIVE_EN.findall(plain))
        passive_ratio = passive_hits / sentence_count if sentence_count else 0.0

    score, formula, verdict, grade = _score(language, avg_sentence_words, avg_syllables, words)

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
