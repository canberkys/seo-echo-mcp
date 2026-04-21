"""generate_slug: title → URL-safe slug with language-aware transliteration."""

from __future__ import annotations

import re
import unicodedata

from seo_echo_mcp.config.slug_rules import STOPWORDS, TRANSLITERATE
from seo_echo_mcp.schemas import SlugResult


async def generate_slug(title: str, language: str = "en", max_length: int = 60) -> SlugResult:
    """Convert a title into a URL-safe slug with two shorter alternatives.

    Uses language-specific character maps first (so Turkish `ı` becomes `i`,
    German `ü` becomes `ue`), then falls back to Unicode NFKD + ASCII filter.

    Args:
        title: Post title in any language.
        language: ISO 639-1 code. Falls back to generic NFKD if unknown.
        max_length: Cap for the primary slug (default 60).

    Returns:
        SlugResult with primary slug and two progressively shorter alternatives
        (one with stopwords removed, one keyword-only truncated).
    """
    primary = _slugify(title, language, max_length=max_length)
    no_stop = _slugify(title, language, max_length=max_length, drop_stopwords=True)
    short = _truncate_slug(no_stop or primary, 40)
    alternatives: list[str] = []
    if no_stop and no_stop != primary:
        alternatives.append(no_stop)
    if short and short not in (primary, no_stop):
        alternatives.append(short)
    return SlugResult(
        primary=primary, alternatives=alternatives, language=language, original_title=title
    )


def _slugify(text: str, language: str, max_length: int, drop_stopwords: bool = False) -> str:
    out = text
    lang_map = TRANSLITERATE.get(language, {})
    for src, dst in lang_map.items():
        out = out.replace(src, dst)
    out = unicodedata.normalize("NFKD", out)
    out = out.encode("ascii", "ignore").decode("ascii")
    out = out.lower()
    out = re.sub(r"[^a-z0-9]+", "-", out).strip("-")
    if drop_stopwords:
        stop = STOPWORDS.get(language, STOPWORDS["en"])
        parts = [p for p in out.split("-") if p and p not in stop]
        out = "-".join(parts)
    out = re.sub(r"-+", "-", out)
    if len(out) > max_length:
        out = _truncate_slug(out, max_length)
    return out


def _truncate_slug(slug: str, limit: int) -> str:
    if len(slug) <= limit:
        return slug
    truncated = slug[:limit].rsplit("-", 1)[0]
    return truncated or slug[:limit]
