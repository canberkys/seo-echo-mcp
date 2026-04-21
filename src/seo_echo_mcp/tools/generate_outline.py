"""generate_outline: deterministic outline synthesis from site + competitor data."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from seo_echo_mcp.config.templates.loader import load as load_templates
from seo_echo_mcp.schemas import CompetitorAnalysis, Outline, OutlineSection, SiteProfile

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
    language = site_profile.language
    tpl = load_templates(language)
    year = str(datetime.now(timezone.utc).year)
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
    keyword_title = keyword.title() if keyword.islower() else keyword

    comp_topics = comp.insights.common_h2_topics if comp and comp.insights else []
    topic_iter = iter(comp_topics)

    purposes = _purposes_for(n)
    sections: list[OutlineSection] = []
    for i in range(n):
        purpose = purposes[i]
        if purpose == "introduction":
            h2 = template_pool[0].format(Keyword=keyword_title, Year=_year())
            must_cover = [
                f"Define {keyword}",
                "Why it matters right now",
                "Who this article is for",
            ]
        elif purpose == "summary":
            h2 = _summary_h2(h2_style, keyword_title)
            must_cover = ["Key takeaways", "Next action for the reader"]
        else:
            topic = next(topic_iter, None)
            if topic:
                h2 = _format_h2(h2_style, f"{keyword_title} and {topic}")
                must_cover = [
                    f"Explain the role of {topic} in {keyword}",
                    "Concrete examples",
                    "Common pitfalls",
                ]
            else:
                tmpl = template_pool[(i) % len(template_pool)]
                h2 = tmpl.format(Keyword=keyword_title, Year=_year())
                must_cover = [
                    f"Core concept around {keyword}",
                    "Practical application",
                    "Example or case",
                ]
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


def _purposes_for(n: int) -> list[str]:
    if n <= 2:
        return ["introduction", "summary"][:n]
    return ["introduction", *["core"] * (n - 2), "summary"]


def _format_h2(style: str, base: str) -> str:
    if style == "question":
        return f"What is {base}?"
    if style == "imperative":
        return f"Master {base}"
    return base


def _summary_h2(style: str, keyword_title: str) -> str:
    if style == "question":
        return f"What should you do next with {keyword_title}?"
    if style == "imperative":
        return f"Put {keyword_title} into practice"
    return f"{keyword_title}: key takeaways"


def _visuals_for(purpose: str) -> list[str]:
    if purpose == "introduction":
        return ["hero image", "context diagram"]
    if purpose == "summary":
        return ["key-takeaways card"]
    return ["diagram", "screenshot"]


def _fill_titles(templates: list[str], keyword: str, year: str, n: int) -> list[str]:
    out: list[str] = []
    for tmpl in templates[:n]:
        out.append(
            tmpl.format(Keyword=keyword.title() if keyword.islower() else keyword, Year=year, N=5)
        )
    while len(out) < n:
        out.append(f"{keyword} — {year}")
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
