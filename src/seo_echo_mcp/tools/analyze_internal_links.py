"""analyze_internal_links: internal link audit for a markdown draft."""

from __future__ import annotations

import logging
import re

from seo_echo_mcp.schemas import (
    InternalLinkOpportunity,
    InternalLinkReport,
    SiteProfile,
)
from seo_echo_mcp.utils.text import split_headings, strip_frontmatter

logger = logging.getLogger(__name__)

_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
_BARE_URL_RE = re.compile(r"(?<!\()\bhttps?://\S+")
_MIN_OPPORTUNITY_TOKENS = 2


async def analyze_internal_links(
    content_markdown: str,
    site_profile: SiteProfile,
) -> InternalLinkReport:
    """Audit internal linking in a markdown draft.

    Finds all links in the draft, splits them into internal vs external,
    identifies which existing posts are already linked, surfaces posts that
    share topic tokens with the draft but aren't linked yet (opportunities),
    and flags H2 sections that contain no links at all.

    Args:
        content_markdown: Full markdown draft (frontmatter tolerated).
        site_profile: SiteProfile from analyze_site — provides the domain and
            existing posts list for opportunity matching.

    Returns:
        InternalLinkReport with counts, opportunities, and recommendations.
    """
    if not content_markdown or not content_markdown.strip():
        raise ValueError("`content_markdown` must be a non-empty string.")

    body = strip_frontmatter(content_markdown)
    domain = site_profile.domain

    # --- Extract all links ---
    md_links = _LINK_RE.findall(body)  # (text, url) pairs
    md_urls = {url for _, url in md_links}
    bare_urls = set(_BARE_URL_RE.findall(body)) - md_urls
    all_urls = md_urls | bare_urls

    internal_urls = {u for u in all_urls if domain in u}
    external_urls = all_urls - internal_urls

    # --- Which existing posts are already linked? ---
    existing_url_set = {p.url for p in site_profile.existing_posts}
    linked_post_urls = [u for u in internal_urls if u in existing_url_set]

    # --- Unlinked opportunities: token overlap between draft and post title ---
    draft_tokens = _tokenize(body)
    unlinked: list[InternalLinkOpportunity] = []
    for post in site_profile.existing_posts:
        if post.url in linked_post_urls:
            continue
        post_tokens = _tokenize(f"{post.title} {' '.join(post.h2s)}")
        shared = draft_tokens & post_tokens
        if len(shared) >= _MIN_OPPORTUNITY_TOKENS:
            unlinked.append(
                InternalLinkOpportunity(
                    existing_url=post.url,
                    existing_title=post.title,
                    relevance_reason=f"shared terms: {', '.join(sorted(shared)[:5])}",
                )
            )
    # Sort by number of shared tokens (approximated by reason length as proxy).
    unlinked.sort(key=lambda o: -o.relevance_reason.count(","))

    # --- Sections without links ---
    sections_without_links = _sections_lacking_links(body)

    # --- Density score ---
    score = _density_score(
        internal=len(internal_urls),
        opportunities=len(unlinked),
        sections_bare=len(sections_without_links),
        total_sections=len(_get_h2s(body)),
    )

    recommendations = _build_recommendations(
        internal=len(internal_urls),
        external=len(external_urls),
        unlinked=unlinked,
        sections_without_links=sections_without_links,
    )

    logger.info(
        "analyze_internal_links domain=%s internal=%d external=%d opportunities=%d score=%d",
        domain,
        len(internal_urls),
        len(external_urls),
        len(unlinked),
        score,
    )

    return InternalLinkReport(
        total_links=len(all_urls),
        internal_links=len(internal_urls),
        external_links=len(external_urls),
        linked_post_urls=linked_post_urls,
        unlinked_opportunities=unlinked[:10],
        sections_without_links=sections_without_links,
        link_density_score=score,
        recommendations=recommendations,
    )


def _tokenize(text: str) -> set[str]:
    _STOP = {
        "the", "a", "an", "and", "or", "of", "to", "for", "with", "in", "on",
        "is", "are", "was", "were", "be", "been", "how", "what", "why", "when",
        "de", "la", "le", "el", "und", "ve", "bir", "bu", "için",
    }
    tokens = re.findall(r"[a-zA-ZÀ-ÿĀ-ɏЀ-ӿ]{4,}", text.lower())
    return {t for t in tokens if t not in _STOP}


def _get_h2s(body: str) -> list[str]:
    _, h2s, _ = split_headings(body)
    return h2s


def _sections_lacking_links(body: str) -> list[str]:
    """Return H2 headings whose section body contains no hyperlink."""
    lines = body.splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_h2: str | None = None
    current_lines: list[str] = []

    for line in lines:
        m = re.match(r"^##\s+(.*?)\s*$", line)
        if m:
            if current_h2 is not None:
                sections.append((current_h2, current_lines))
            current_h2 = m.group(1)
            current_lines = []
        else:
            if current_h2 is not None:
                current_lines.append(line)

    if current_h2 is not None:
        sections.append((current_h2, current_lines))

    bare: list[str] = []
    for h2, section_lines in sections:
        section_text = "\n".join(section_lines)
        has_link = bool(_LINK_RE.search(section_text) or _BARE_URL_RE.search(section_text))
        if not has_link:
            bare.append(h2)
    return bare


def _density_score(
    internal: int,
    opportunities: int,
    sections_bare: int,
    total_sections: int,
) -> int:
    score = 100
    # Penalise low internal link count
    if internal == 0:
        score -= 40
    elif internal < 2:
        score -= 20
    elif internal < 4:
        score -= 10
    # Penalise missed opportunities (capped)
    score -= min(opportunities * 5, 25)
    # Penalise sections without links
    if total_sections > 0:
        bare_ratio = sections_bare / total_sections
        score -= int(bare_ratio * 20)
    return max(0, score)


def _build_recommendations(
    internal: int,
    external: int,
    unlinked: list[InternalLinkOpportunity],
    sections_without_links: list[str],
) -> list[str]:
    recs: list[str] = []
    if internal == 0:
        recs.append("No internal links found — add at least 2-3 links to related posts.")
    elif internal < 2:
        recs.append(f"Only {internal} internal link(s) — aim for 2-4 per 1000 words.")
    if external < 1:
        recs.append("No external citations — add at least one authoritative external link.")
    for opp in unlinked[:3]:
        recs.append(
            f"Link to '{opp.existing_title}' ({opp.existing_url}) — {opp.relevance_reason}."
        )
    if sections_without_links:
        bare = ", ".join(f'"{h}"' for h in sections_without_links[:3])
        recs.append(f"Sections with no links: {bare} — add a relevant link in each.")
    return recs[:8]
