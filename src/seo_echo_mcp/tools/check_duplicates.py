"""check_duplicates: flag existing posts that overlap with a proposed keyword/title."""

from __future__ import annotations

import re
from typing import Literal

from seo_echo_mcp.schemas import DuplicateMatch, DuplicateReport, SiteProfile

_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "for", "with", "in", "on",
    "ve", "ile", "bir", "bu", "için", "olan", "nedir",
    "el", "la", "los", "las", "de", "del", "y",
    "le", "les", "du", "des", "et",
    "der", "die", "das", "und",
}


async def check_duplicates(
    proposed: str,
    site_profile: SiteProfile,
    threshold: float = 0.3,
) -> DuplicateReport:
    """Detect whether the proposed keyword/title overlaps with existing posts.

    Uses Jaccard similarity over stopword-filtered tokens. Any post above
    `threshold` is flagged; the verdict escalates to "duplicate" at 0.6+.

    Args:
        proposed: Proposed keyword or title for the new piece.
        site_profile: SiteProfile from analyze_site (uses `existing_posts`).
        threshold: Minimum overlap score to flag (default 0.30 = 30%).

    Returns:
        DuplicateReport with matches, scores, and an overall verdict.
    """
    proposed_tokens = _tokenize(proposed)
    if not proposed_tokens:
        return DuplicateReport(proposed=proposed, matches=[], verdict="safe")

    matches: list[DuplicateMatch] = []
    for post in site_profile.existing_posts:
        haystack = f"{post.title} {post.snippet}"
        post_tokens = _tokenize(haystack)
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


def _tokenize(text: str) -> set[str]:
    raw = re.findall(r"[\w]{3,}", text.lower())
    return {t for t in raw if t not in _STOP}


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
