"""check_duplicates: flag existing posts that overlap with a proposed keyword/title."""

from __future__ import annotations

import logging
import re
from typing import Literal

from seo_echo_mcp.schemas import DuplicateMatch, DuplicateReport, SiteProfile
from seo_echo_mcp.utils.text import stem_tr

logger = logging.getLogger(__name__)

_STOP = {
    # English
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "for",
    "with",
    "in",
    "on",
    "what",
    "how",
    "why",
    "when",
    "where",
    "which",
    "who",
    # Turkish — include common question/connective words so they don't
    # dominate Jaccard scores on short titles.
    "ve",
    "ile",
    "bir",
    "bu",
    "şu",
    "için",
    "olan",
    "gibi",
    "kadar",
    "nedir",
    "nasıl",
    "nas",
    "neden",
    "nerede",
    "niçin",
    "hangi",
    "hangisi",
    "hakkınd",
    "hakkında",
    "yönetim",
    "ilgili",
    # Spanish
    "el",
    "la",
    "los",
    "las",
    "de",
    "del",
    "y",
    "un",
    "una",
    "que",
    # French
    "le",
    "les",
    "du",
    "des",
    "et",
    "une",
    "qui",
    "quoi",
    # German
    "der",
    "die",
    "das",
    "und",
    "ein",
    "eine",
    "wer",
    "was",
}


async def check_duplicates(
    proposed: str,
    site_profile: SiteProfile,
    threshold: float = 0.3,
) -> DuplicateReport:
    """Detect whether the proposed keyword/title overlaps with existing posts.

    Uses Jaccard similarity over stopword-filtered, optionally stemmed tokens.
    Any post above `threshold` is flagged; the verdict escalates to "duplicate"
    at 0.6+.

    For Turkish sites, tokens are stemmed with a simple suffix trimmer so
    "snapshot'ları" and "snapshot" collapse to the same token.

    Args:
        proposed: Proposed keyword or title for the new piece.
        site_profile: SiteProfile from analyze_site (uses `existing_posts`).
        threshold: Minimum overlap score to flag (default 0.30 = 30%).

    Returns:
        DuplicateReport with matches, scores, and an overall verdict.
    """
    if not proposed or not proposed.strip():
        raise ValueError("`proposed` must be a non-empty string.")
    language = site_profile.language
    proposed_tokens = _tokenize(proposed, language)
    logger.info(
        "check_duplicates proposed=%r lang=%s existing=%d",
        proposed,
        language,
        len(site_profile.existing_posts),
    )
    if not proposed_tokens:
        return DuplicateReport(proposed=proposed, matches=[], verdict="safe")

    matches: list[DuplicateMatch] = []
    for post in site_profile.existing_posts:
        haystack = f"{post.title} {post.snippet}"
        post_tokens = _tokenize(haystack, language)
        if not post_tokens:
            continue
        score = _jaccard(proposed_tokens, post_tokens)
        if score >= threshold:
            matches.append(
                DuplicateMatch(
                    existing_url=post.url,
                    existing_title=post.title,
                    overlap_score=round(score, 3),
                    reason=_reason(score),
                )
            )
    matches.sort(key=lambda m: -m.overlap_score)
    verdict: Literal["safe", "caution", "duplicate"] = _verdict(matches)
    return DuplicateReport(proposed=proposed, matches=matches, verdict=verdict)


def _tokenize(text: str, language: str = "en") -> set[str]:
    # Keep apostrophe-suffixes attached so stem_tr can strip them ('larını, etc.)
    raw = re.findall(r"[\w']{3,}", text.lower())
    stop = _STOP
    if language == "tr":
        return {stem_tr(t) for t in raw if stem_tr(t) not in stop}
    return {t for t in raw if t not in stop}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _reason(score: float) -> str:
    if score >= 0.6:
        return "Very high token overlap — likely covers the same topic."
    if score >= 0.45:
        return "High overlap — merge or repurpose rather than create a new post."
    return "Moderate overlap — ensure the angle is distinct."


def _verdict(matches: list[DuplicateMatch]) -> Literal["safe", "caution", "duplicate"]:
    if not matches:
        return "safe"
    top = matches[0].overlap_score
    if top >= 0.6:
        return "duplicate"
    if top >= 0.45:
        return "caution"
    return "caution"
