"""generate_outline: deterministic outline synthesis from site + competitor data."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

from seo_echo_mcp.config.templates.loader import load as load_templates
from seo_echo_mcp.schemas import CompetitorAnalysis, Outline, OutlineSection, SiteProfile

logger = logging.getLogger(__name__)

_MIN_SECTIONS = 5
_MAX_SECTIONS = 12
_WORDS_PER_SECTION = 250


async def generate_outline(
    keyword: str,
    site_profile: SiteProfile,
    competitor_analysis: CompetitorAnalysis | None = None,
    target_word_count: int | None = None,
    new_category: str | None = None,
) -> Outline:
    """Produce an SEO outline tailored to a site's voice and competitor context.

    Purely rule-based — this tool does NOT call any LLM. Its output is meant to
    be fed to the host LLM (Claude, Cursor, etc.) to actually write prose.

    Args:
        keyword: Target keyword/phrase for the new article.
        site_profile: Result of `analyze_site`.
        competitor_analysis: Optional result of `analyze_competitors`. If omitted,
            outline is more generic.
        target_word_count: Override for section count; defaults to site average.
        new_category: Override category context (for expanding into new topics).

    Returns:
        Outline with 5-12 sections, 3 title candidates, 3 meta descriptions,
        internal link targets, and citation-research topic stubs.
    """
    if not keyword or not keyword.strip():
        raise ValueError("`keyword` must be a non-empty string.")
    language = site_profile.language
    tpl = load_templates(language)
    year = str(datetime.now(timezone.utc).year)
    logger.info(
        "generate_outline keyword=%r lang=%s target_wc=%s", keyword, language, target_word_count
    )
    category = new_category or (
        site_profile.categories[0] if site_profile.categories else "general"
    )
    addressing = site_profile.style.addressing
    h2_style = site_profile.style.h2_pattern
    word_count_target = target_word_count or site_profile.style.average_word_count or 1200
    section_count = max(_MIN_SECTIONS, min(_MAX_SECTIONS, word_count_target // _WORDS_PER_SECTION))

    sections = _build_sections(
        keyword, tpl, h2_style, competitor_analysis, section_count, word_count_target
    )
    titles = _fill_titles(tpl.TITLE_TEMPLATES, keyword, year, n=3)
    metas = _fill_metas(tpl.META_TEMPLATES, keyword, year)
    internal_link_targets = _select_internal_links(site_profile, keyword, k=5)
    citation_topics = _citation_topics(keyword, year)

    return Outline(
        keyword=keyword,
        language=language,
        suggested_titles=titles,
        suggested_meta_descriptions=metas,
        word_count_target=word_count_target,
        h2_style=h2_style,
        addressing=addressing,
        category=category,
        sections=sections,
        recommended_internal_link_targets=internal_link_targets,
        external_citation_topics=citation_topics,
        cta_suggestion=tpl.CTA,
    )


def _build_sections(
    keyword: str,
    tpl,
    h2_style: str,
    comp: CompetitorAnalysis | None,
    n: int,
    total_words: int,
) -> list[OutlineSection]:
    per_section = max(150, total_words // n)

    template_pool = tpl.H2_TEMPLATES.get(h2_style, tpl.H2_TEMPLATES["statement"])
    # Preserve user-supplied casing — users write "VMware vMotion" correctly;
    # `.title()` would produce "Vmware Vmotion".
    keyword_display = keyword

    comp_topics = comp.insights.common_h2_topics if comp and comp.insights else []
    topic_iter = iter(comp_topics)

    purposes = _purposes_for(n)
    sections: list[OutlineSection] = []
    used_h2s: set[str] = set()
    for i in range(n):
        purpose = purposes[i]
        if purpose == "introduction":
            h2 = template_pool[0].format(Keyword=keyword_display, Year=_year())
            must_cover = [item.format(keyword=keyword) for item in tpl.MUST_COVER_INTRO]
        elif purpose == "summary":
            h2 = _summary_h2(tpl, h2_style, keyword_display)
            must_cover = [item.format(keyword=keyword) for item in tpl.MUST_COVER_SUMMARY]
        else:
            topic = next(topic_iter, None)
            if topic:
                joined = f"{keyword_display} {tpl.TOPIC_CONNECTOR} {topic}"
                h2 = _format_h2(tpl, h2_style, joined)
                must_cover = [
                    item.format(keyword=keyword, topic=topic) for item in tpl.MUST_COVER_TOPIC
                ]
            else:
                h2 = _pick_unused_template(
                    template_pool, keyword_display, used_h2s
                ) or _synthetic_h2(tpl, h2_style, keyword_display, i, used_h2s)
                must_cover = [item.format(keyword=keyword) for item in tpl.MUST_COVER_CORE]
        # Final dedup guard — try alternate synthetic variants before giving up
        if h2 in used_h2s:
            h2 = _synthetic_h2(tpl, h2_style, keyword_display, i, used_h2s)
        used_h2s.add(h2)
        sections.append(
            OutlineSection(
                h2=h2,
                purpose=purpose,
                word_count_target=per_section,
                must_cover=must_cover,
                suggested_visuals=_visuals_for(purpose),
            )
        )
    return sections


def _pick_unused_template(pool: list[str], keyword: str, used: set[str]) -> str | None:
    for tmpl in pool:
        candidate = tmpl.format(Keyword=keyword, Year=_year())
        if candidate not in used:
            return candidate
    return None


def _synthetic_h2(tpl, style: str, keyword: str, index: int, used: set[str] | None = None) -> str:
    """Fallback H2 when the template pool is exhausted.

    Walks the language-specific variant pool (12 entries per language) and
    returns the first candidate not already in `used`. Falls back to a numbered
    suffix only if every variant collides.
    """
    variants = [v.format(Keyword=keyword) for v in tpl.SYNTHETIC_H2_VARIANTS]
    for offset in range(len(variants)):
        base = variants[(index + offset) % len(variants)]
        styled = _apply_h2_style(tpl, style, base)
        if used is None or styled not in used:
            return styled
    # Last resort: numeric suffix to guarantee uniqueness
    base = variants[index % len(variants)]
    return _apply_h2_style(tpl, style, f"{base} ({index + 1})")


def _apply_h2_style(tpl, style: str, base: str) -> str:
    template = tpl.H2_STYLE_TEMPLATES.get(style, "{base}")
    return template.format(base=base)


def _purposes_for(n: int) -> list[str]:
    if n <= 2:
        return ["introduction", "summary"][:n]
    return ["introduction", *["core"] * (n - 2), "summary"]


def _format_h2(tpl, style: str, base: str) -> str:
    return _apply_h2_style(tpl, style, base)


def _summary_h2(tpl, style: str, keyword_display: str) -> str:
    template = tpl.SUMMARY_H2.get(style, tpl.SUMMARY_H2["statement"])
    return template.format(keyword=keyword_display)


def _visuals_for(purpose: str) -> list[str]:
    if purpose == "introduction":
        return ["hero image", "context diagram"]
    if purpose == "summary":
        return ["key-takeaways card"]
    return ["diagram", "screenshot"]


def _fill_titles(templates: list[str], keyword: str, year: str, n: int) -> list[str]:
    out: list[str] = []
    for tmpl in templates[:n]:
        out.append(tmpl.format(Keyword=keyword, Year=year, N=5))
    while len(out) < n:
        out.append(f"{keyword} ({year})")
    return out[:n]


def _fill_metas(templates: list[str], keyword: str, year: str) -> list[str]:
    out: list[str] = []
    for tmpl in templates:
        text = tmpl.format(keyword=keyword, year=year)
        text = _fit_meta_length(text)
        out.append(text)
    return out[:3]


def _fit_meta_length(text: str) -> str:
    if len(text) >= 140 and len(text) <= 160:
        return text
    if len(text) < 140:
        return (
            text
            + " "
            + ("Learn the essentials today." if not text.endswith(".") else "Learn more today.")
        )
    return text[:157].rstrip() + "…"


def _select_internal_links(site: SiteProfile, keyword: str, k: int) -> list[str]:
    needle = keyword.lower()
    scored: list[tuple[int, str]] = []
    for p in site.existing_posts:
        haystack = (p.title + " " + p.snippet).lower()
        hits = sum(1 for word in needle.split() if word and word in haystack)
        if hits:
            scored.append((hits, p.url))
    scored.sort(reverse=True)
    return [u for _, u in scored[:k]]


def _citation_topics(keyword: str, year: str) -> list[str]:
    return [
        f"Recent {year} statistics on {keyword}",
        f"Case studies involving {keyword}",
        f"Expert opinions or interviews about {keyword}",
    ]


def _year() -> str:
    return str(datetime.now(timezone.utc).year)


# Remove import-time dependency on module-level regex usage
_HAS_DIGIT = re.compile(r"\d")
