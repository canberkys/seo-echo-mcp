"""generate_meta_variations: 5 meta descriptions, one per angle."""

from __future__ import annotations

from datetime import datetime, timezone

from seo_echo_mcp.config.seo_rules import META_DESC_MAX, META_DESC_MIN
from seo_echo_mcp.config.templates.loader import load as load_templates
from seo_echo_mcp.schemas import MetaVariation, MetaVariations


async def generate_meta_variations(
    keyword: str, title: str, language: str = "en"
) -> MetaVariations:
    """Return 5 meta descriptions (140-160 char band), one per angle.

    Angles: problem-solution, question, benefit, curiosity, action.

    Args:
        keyword: Target keyword (used verbatim inside the description).
        title: Post title (kept for downstream UIs that render title+meta pairs).
        language: ISO 639-1 code.

    Returns:
        MetaVariations with 5 MetaVariation entries, length and keyword presence
        tracked per item.
    """
    tpl = load_templates(language)
    year = str(datetime.now(timezone.utc).year)
    angles = ["problem-solution", "question", "benefit", "curiosity", "action"]
    items: list[MetaVariation] = []
    for angle in angles:
        template = tpl.META_ANGLES.get(angle, "{keyword} — {year}")
        text = template.format(keyword=keyword, year=year)
        text = _fit_length(text)
        items.append(
            MetaVariation(
                description=text,
                angle=angle,  # type: ignore[arg-type]
                length=len(text),
                keyword_present=keyword.lower() in text.lower(),
            )
        )
    return MetaVariations(keyword=keyword, title=title, language=language, items=items)


def _fit_length(text: str) -> str:
    if META_DESC_MIN <= len(text) <= META_DESC_MAX:
        return text
    if len(text) > META_DESC_MAX:
        return text[: META_DESC_MAX - 1].rstrip() + "…"
    filler = " Read the full guide."
    while len(text) < META_DESC_MIN and len(text + filler) <= META_DESC_MAX:
        text = text + filler
    return text
