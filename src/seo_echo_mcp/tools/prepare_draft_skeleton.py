"""prepare_draft_skeleton: turn an Outline into a full markdown skeleton.

The output is the central artifact of the content workflow: a markdown file
with YAML frontmatter, H2 sections, `<!-- WRITE: ... -->` directives that
instruct the host LLM exactly what to write (word count, tone, addressing,
must-cover points), citation slots, internal link placeholders, optional FAQ
block, and optional JSON-LD. The host LLM replaces each directive with prose
and saves the final `.md` to disk with its Write tool.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from seo_echo_mcp.config.templates.loader import load as load_templates
from seo_echo_mcp.schemas import (
    DraftSkeleton,
    FaqSection,
    Outline,
    SchemaJsonLd,
    SiteProfile,
    apply_voice_overrides,
)
from seo_echo_mcp.tools.generate_slug import generate_slug

logger = logging.getLogger(__name__)


async def prepare_draft_skeleton(
    outline: Outline,
    site_profile: SiteProfile,
    target_keyword: str | None = None,
    slug: str | None = None,
    faq_section: FaqSection | None = None,
    schema_jsonld: SchemaJsonLd | None = None,
    selected_title_index: int = 0,
    selected_meta_index: int = 0,
    voice_overrides: dict | None = None,
) -> DraftSkeleton:
    """Assemble a full markdown skeleton ready for the host LLM to fill.

    Args:
        outline: Result of generate_outline.
        site_profile: Result of analyze_site (used for voice directives).
        target_keyword: Keyword to embed in the frontmatter; defaults to outline.keyword.
        slug: Pre-computed slug; if omitted, generate_slug is called internally.
        faq_section: Optional FaqSection from generate_faq_section (embedded verbatim).
        schema_jsonld: Optional SchemaJsonLd from generate_schema_jsonld (embedded as comment).
        selected_title_index: Which of outline.suggested_titles to use (default 0).
        selected_meta_index: Which of outline.suggested_meta_descriptions to use (default 0).
        voice_overrides: Optional dict to override StyleProfile fields only for this
            skeleton (e.g. `{"em_dash_frequency": "never"}`). The directive text
            handed to the host LLM reflects the overridden values.

    Returns:
        DraftSkeleton with the full markdown, frontmatter dict, and metadata.
    """
    site_profile = apply_voice_overrides(site_profile, voice_overrides)
    keyword = target_keyword or outline.keyword
    language = outline.language
    load_templates(language)  # validate language is supported / preload module
    logger.info(
        "prepare_draft_skeleton keyword=%r lang=%s sections=%d has_faq=%s has_schema=%s",
        keyword,
        language,
        len(outline.sections),
        faq_section is not None,
        schema_jsonld is not None,
    )

    title = _safe_pick(outline.suggested_titles, selected_title_index, f"{keyword}")
    meta_description = _safe_pick(
        outline.suggested_meta_descriptions, selected_meta_index, f"Guide to {keyword}."
    )
    if slug is None:
        slug_result = await generate_slug(title, language=language)
        slug = slug_result.primary

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    frontmatter = {
        "title": title,
        "description": meta_description,
        "slug": slug,
        "category": outline.category,
        "keyword": keyword,
        "language": language,
        "date": now,
    }

    voice_directive = _voice_directive(site_profile)
    body_parts: list[str] = []
    body_parts.append(_frontmatter_block(frontmatter))
    body_parts.append(f"# {title}\n")
    body_parts.append(
        f"<!-- WRITE intro: 120-180 words. {voice_directive} "
        f"Include target keyword '{keyword}' in the first sentence. "
        "State the problem, who this is for, and what the reader will learn. -->"
    )
    body_parts.append("")

    for i, section in enumerate(outline.sections, start=1):
        body_parts.append(f"## {section.h2}")
        body_parts.append("")
        must_cover = ", ".join(section.must_cover) if section.must_cover else "core explanation"
        visuals = ", ".join(section.suggested_visuals) if section.suggested_visuals else "optional"
        body_parts.append(
            f"<!-- WRITE section {i} ({section.purpose}): {section.word_count_target} words. "
            f"{voice_directive} "
            f"Must cover: {must_cover}. Suggested visuals: {visuals}. -->"
        )
        if i == 2 and outline.recommended_internal_link_targets:
            link = outline.recommended_internal_link_targets[0]
            body_parts.append("")
            body_parts.append(f"<!-- LINK: weave in an internal link to {link} -->")
        if outline.external_citation_topics and i == len(outline.sections) // 2:
            topic = outline.external_citation_topics[0]
            body_parts.append("")
            body_parts.append(f"<!-- CITE: {topic} -->")
        body_parts.append("")

    if faq_section:
        body_parts.append(faq_section.markdown.rstrip())
        body_parts.append("")

    body_parts.append(f"<!-- CTA: {outline.cta_suggestion} -->")
    body_parts.append("")

    if schema_jsonld:
        body_parts.append("<!-- Paste the following JSON-LD in your page <head> before publishing:")
        body_parts.append(schema_jsonld.html_snippet)
        body_parts.append("-->")

    if faq_section:
        body_parts.append("")
        body_parts.append("<!-- Paste the FAQPage JSON-LD in <head> as well:")
        body_parts.append(
            f'<script type="application/ld+json">\n{faq_section.faq_jsonld}\n</script>'
        )
        body_parts.append("-->")

    markdown = "\n".join(body_parts).rstrip() + "\n"

    return DraftSkeleton(
        keyword=keyword,
        language=language,
        slug=slug,
        frontmatter=frontmatter,
        markdown=markdown,
        word_count_target=outline.word_count_target,
        section_count=len(outline.sections),
        has_faq=faq_section is not None,
        has_schema=schema_jsonld is not None,
    )


def _safe_pick(items: list[str], idx: int, fallback: str) -> str:
    if not items:
        return fallback
    if 0 <= idx < len(items):
        return items[idx]
    return items[0]


def _voice_directive(site: SiteProfile) -> str:
    addressing = site.style.addressing
    tone = site.style.tone
    em = site.style.em_dash_frequency
    avg_sent = site.style.avg_sentence_words
    parts = [
        f"Tone: {tone}.",
        f"Addressing: '{addressing}'.",
        f"Avg sentence ~{avg_sent:.0f} words.",
    ]
    if em == "never":
        parts.append("Do NOT use em-dashes (—).")
    elif em == "rare":
        parts.append("Use em-dashes sparingly (<5 total).")
    if site.style.uses_lists:
        parts.append("Use bullet lists when helpful.")
    if site.style.uses_code_blocks:
        parts.append("Include code blocks when showing commands.")
    return " ".join(parts)


def _frontmatter_block(fm: dict) -> str:
    lines = ["---"]
    for key, value in fm.items():
        escaped = str(value).replace('"', '\\"')
        lines.append(f'{key}: "{escaped}"')
    lines.append("---")
    lines.append("")
    return "\n".join(lines)
