"""suggest_titles: generate SEO-aware title candidates matched to site voice."""

from __future__ import annotations

import logging
import re
from collections import Counter
from datetime import datetime, timezone

from seo_echo_mcp.config.templates.loader import load as load_templates
from seo_echo_mcp.schemas import (
    CompetitorAnalysis,
    SiteProfile,
    TitleSuggestion,
    TitleSuggestions,
)

logger = logging.getLogger(__name__)

_SERP_CHAR_LIMIT = 60
_PATTERNS_ORDER = (
    "how-to",
    "question",
    "listicle",
    "comparison",
    "year",
    "benefit",
    "curiosity",
    "statement",
)
_DEFAULT_LISTICLE_N = 7


async def suggest_titles(
    keyword: str,
    site_profile: SiteProfile,
    competitor_analysis: CompetitorAnalysis | None = None,
    count: int = 10,
) -> TitleSuggestions:
    """Produce ranked title candidates for a keyword.

    Ordering rules:
      1. Titles whose pattern matches the site's H2 pattern are ranked higher.
      2. Patterns that dominate competitor titles get a small boost.
      3. Within a pattern, templates are used in the order defined per language.

    Args:
        keyword: Target keyword/phrase.
        site_profile: SiteProfile from analyze_site.
        competitor_analysis: Optional CompetitorAnalysis to bias toward formats
            that are working in SERP (e.g. listicles, guides).
        count: Number of suggestions to return (default 10).

    Returns:
        TitleSuggestions with ranked items and a primary recommendation.
    """
    if not keyword or not keyword.strip():
        raise ValueError("`keyword` must be a non-empty string.")
    tpl = load_templates(site_profile.language)
    year = str(datetime.now(timezone.utc).year)
    # Preserve user casing — users write "VMware vMotion" correctly.
    keyword_display = keyword
    logger.info(
        "suggest_titles keyword=%r lang=%s count=%d",
        keyword,
        site_profile.language,
        count,
    )

    dominant = competitor_analysis.insights.dominant_format if competitor_analysis else None
    site_pattern = site_profile.style.h2_pattern
    listicle_n = _competitor_listicle_n(competitor_analysis)

    ordered_patterns = _rank_patterns(site_pattern, dominant)
    items: list[TitleSuggestion] = []
    seen_titles: set[str] = set()
    for pattern in ordered_patterns:
        templates = tpl.TITLE_VARIANT_TEMPLATES.get(pattern, [])
        for template in templates:
            title = template.format(Keyword=keyword_display, Year=year, N=listicle_n)
            if title in seen_titles:
                continue
            seen_titles.add(title)
            items.append(
                TitleSuggestion(
                    title=title,
                    length=len(title),
                    pattern=pattern,  # type: ignore[arg-type]
                    serp_safe=len(title) <= _SERP_CHAR_LIMIT,
                    matches_site_style=_matches_site(pattern, site_pattern),
                )
            )
            if len(items) >= count:
                break
        if len(items) >= count:
            break

    items = items[:count]
    primary = items[0].title if items else keyword_display
    return TitleSuggestions(
        keyword=keyword, language=site_profile.language, items=items, primary_recommendation=primary
    )


def _competitor_listicle_n(comp: CompetitorAnalysis | None) -> int:
    """Most common integer appearing in competitor titles, for listicle parity.

    Falls back to 7 when unavailable. This makes suggested listicles ("Top N X")
    match the count SERP competitors are already using — readers and search
    engines expect a similar shape.
    """
    if not comp or not comp.results:
        return _DEFAULT_LISTICLE_N
    numbers: list[int] = []
    for r in comp.results:
        for match in re.findall(r"\b(\d{1,3})\b", r.title or ""):
            n = int(match)
            if 3 <= n <= 50:  # listicle-reasonable range
                numbers.append(n)
    if not numbers:
        return _DEFAULT_LISTICLE_N
    return Counter(numbers).most_common(1)[0][0]


def _rank_patterns(site_pattern: str, dominant: str | None) -> list[str]:
    ordered = list(_PATTERNS_ORDER)
    if site_pattern == "question" and "question" in ordered:
        ordered.remove("question")
        ordered.insert(0, "question")
    if site_pattern == "imperative" and "how-to" in ordered:
        ordered.remove("how-to")
        ordered.insert(0, "how-to")
    if dominant == "listicle" and "listicle" in ordered:
        ordered.remove("listicle")
        ordered.insert(0, "listicle")
    if dominant == "comparison" and "comparison" in ordered:
        ordered.remove("comparison")
        ordered.insert(0, "comparison")
    return ordered


def _matches_site(pattern: str, site_pattern: str) -> bool:
    if site_pattern == "question" and pattern == "question":
        return True
    if site_pattern == "imperative" and pattern == "how-to":
        return True
    return site_pattern == "statement" and pattern in ("statement", "benefit", "year")
