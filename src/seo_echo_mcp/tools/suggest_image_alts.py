"""suggest_image_alts: flag weak/missing alt text and propose replacements."""

from __future__ import annotations

import re
from pathlib import PurePosixPath
from urllib.parse import urlparse

from seo_echo_mcp.schemas import ImageAltReport, ImageAltSuggestion
from seo_echo_mcp.utils.text import markdown_to_plain, strip_frontmatter

_IMG_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)(?:\s+\"[^\"]*\")?\)")
_WEAK_ALTS = {"image", "img", "picture", "photo", "screenshot", "logo", "icon"}
_MIN_ALT_WORDS = 2


async def suggest_image_alts(
    content_markdown: str, target_keyword: str | None = None, language: str = "en"
) -> ImageAltReport:
    """Scan markdown images, flag missing/weak alts, and suggest replacements.

    Alt text quality rules:
      - `missing`: `![](url)` or alt text empty after strip.
      - `weak`: alt is a generic word ("image", "screenshot"), shorter than
        two words, or purely the filename.
      - `ok`: otherwise.

    Suggestions are derived from: (1) the filename's slug stem, (2) the keyword
    if provided, and (3) the nearest preceding paragraph/heading. No LLM call.

    Args:
        content_markdown: Markdown body (frontmatter tolerated).
        target_keyword: Optional keyword to fold into suggestions.
        language: ISO 639-1 code — reserved for future per-language tweaks.

    Returns:
        ImageAltReport with one ImageAltSuggestion per image.
    """
    body = strip_frontmatter(content_markdown)
    items: list[ImageAltSuggestion] = []
    for position, match in enumerate(_IMG_RE.finditer(body), start=1):
        alt = match.group("alt").strip()
        src = match.group("src").strip()
        status = _classify(alt, src)
        context = _context_before(body, match.start())
        suggestions = _build_suggestions(
            filename_stem=_stem_from_src(src),
            keyword=target_keyword,
            context=context,
            existing_alt=alt,
            language=language,
        )
        items.append(
            ImageAltSuggestion(
                position=position,
                src=src,
                current_alt=alt,
                status=status,
                suggested_alts=suggestions,
                context_snippet=context[:200],
            )
        )

    missing = sum(1 for i in items if i.status == "missing")
    weak = sum(1 for i in items if i.status == "weak")
    return ImageAltReport(
        image_count=len(items),
        missing_count=missing,
        weak_count=weak,
        items=items,
    )


def _classify(alt: str, src: str) -> str:
    if not alt:
        return "missing"
    lowered = alt.lower().strip()
    if lowered in _WEAK_ALTS:
        return "weak"
    stem = _stem_from_src(src).lower()
    if stem and lowered == stem:
        return "weak"
    if len(re.findall(r"\S+", alt)) < _MIN_ALT_WORDS:
        return "weak"
    return "ok"


def _stem_from_src(src: str) -> str:
    parsed = urlparse(src)
    name = PurePosixPath(parsed.path or src).stem
    # Strip hashes / version suffixes
    name = re.sub(r"[-_](v\d+|\d{3,}|[a-f0-9]{6,})$", "", name)
    name = re.sub(r"[-_]+", " ", name).strip()
    return name


def _context_before(body: str, offset: int) -> str:
    start = max(0, offset - 400)
    chunk = body[start:offset]
    plain = markdown_to_plain(chunk)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", plain) if p.strip()]
    if paragraphs:
        return paragraphs[-1]
    return plain.strip()


def _build_suggestions(
    filename_stem: str,
    keyword: str | None,
    context: str,
    existing_alt: str,
    language: str,
) -> list[str]:
    pieces: list[str] = []
    stem_clean = filename_stem.strip()
    if stem_clean:
        pieces.append(stem_clean.capitalize())
    if keyword:
        kw = keyword.strip()
        if kw and (not stem_clean or kw.lower() not in stem_clean.lower()):
            pieces.append(kw)
            if stem_clean:
                pieces.append(f"{kw} — {stem_clean}")
    # Derive a topic cue from the nearest heading or sentence in the context
    topic = _topic_from_context(context)
    if topic:
        if keyword:
            pieces.append(f"{keyword}: {topic}")
        else:
            pieces.append(topic)
    # Filter: drop empties + duplicates while preserving order
    seen: set[str] = set()
    out: list[str] = []
    for p in pieces:
        cleaned = re.sub(r"\s+", " ", p).strip().strip("-—:")
        if not cleaned or cleaned.lower() in seen:
            continue
        if existing_alt and cleaned.lower() == existing_alt.lower():
            continue
        seen.add(cleaned.lower())
        out.append(cleaned)
    return out[:3]


def _topic_from_context(context: str) -> str:
    if not context:
        return ""
    # Take the first sentence of the context, trimmed to ~8 words.
    sentence = re.split(r"[.!?]\s", context, maxsplit=1)[0]
    words = sentence.split()
    if len(words) > 8:
        words = words[:8]
    return " ".join(words).strip()
