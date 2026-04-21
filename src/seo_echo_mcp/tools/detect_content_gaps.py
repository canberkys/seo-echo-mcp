"""detect_content_gaps: topics competitors cover but the site doesn't."""

from __future__ import annotations

import re
from collections import defaultdict

from seo_echo_mcp.schemas import CompetitorAnalysis, ContentGap, ContentGapReport, SiteProfile


async def detect_content_gaps(
    site_profile: SiteProfile,
    competitor_analysis: CompetitorAnalysis,
    min_coverage: int = 2,
) -> ContentGapReport:
    """Identify topics that at least `min_coverage` competitors cover but the site misses.

    Topics are inferred from competitor H2 tokens (4+ chars, stopword-filtered),
    compared against the site's existing post titles and topic vocabulary.

    Args:
        site_profile: Result of analyze_site.
        competitor_analysis: Result of analyze_competitors.
        min_coverage: Minimum competitor count that must cover a topic to
            call it a gap (default 2 — avoids noise from unique angles).

    Returns:
        ContentGapReport with per-gap coverage counts and suggested angles.
    """
    site_vocab = _site_vocab(site_profile)
    topic_to_urls: dict[str, set[str]] = defaultdict(set)
    for entry in competitor_analysis.results:
        for h2 in entry.h2s:
            for token in _meaningful_tokens(h2):
                topic_to_urls[token].add(entry.url)

    gaps: list[ContentGap] = []
    for topic, urls in topic_to_urls.items():
        if len(urls) < min_coverage:
            continue
        if topic in site_vocab:
            continue
        gaps.append(
            ContentGap(
                topic=topic,
                coverage_count=len(urls),
                competing_urls=sorted(urls)[:5],
                suggested_angle=_angle_hint(topic, competitor_analysis.keyword or ""),
            )
        )
    gaps.sort(key=lambda g: -g.coverage_count)
    gaps = gaps[:15]

    summary = (
        f"{len(gaps)} topic gap(s) found across {len(competitor_analysis.results)} competitors."
        if gaps
        else "No significant content gaps vs competitors — coverage looks strong."
    )

    return ContentGapReport(
        site_url=site_profile.url,
        keyword_scope=competitor_analysis.keyword,
        gaps=gaps,
        summary=summary,
    )


def _site_vocab(site: SiteProfile) -> set[str]:
    vocab: set[str] = set(t.lower() for t in site.topics)
    for post in site.existing_posts:
        vocab.update(_meaningful_tokens(post.title))
        vocab.update(_meaningful_tokens(post.snippet))
    return vocab


_STOP = {
    "what",
    "how",
    "why",
    "when",
    "where",
    "which",
    "with",
    "from",
    "your",
    "nedir",
    "nasil",
    "nasıl",
    "neden",
    "como",
    "cómo",
    "porque",
    "comment",
    "pourquoi",
    "warum",
    "wie",
}


def _meaningful_tokens(text: str) -> set[str]:
    tokens = re.findall(r"[\w]{4,}", text.lower())
    return {t for t in tokens if t not in _STOP}


def _angle_hint(topic: str, keyword: str) -> str:
    if keyword:
        return (
            f"Explore '{topic}' in the context of '{keyword}' — competitors cover it but you don't."
        )
    return f"Write a focused piece on '{topic}'."
