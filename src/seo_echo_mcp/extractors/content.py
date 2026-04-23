"""HTML → structured post extraction.

Uses trafilatura for main text (handles multilingual boilerplate removal) and
selectolax for fast DOM queries (titles, h2s, meta, published date).
"""

from __future__ import annotations

import json
import re
from typing import Any, TypedDict

import trafilatura
from selectolax.parser import HTMLParser


class ExtractedPost(TypedDict):
    """Shape returned by `extract_content` — one blog post."""

    title: str
    main_text: str
    word_count: int
    h2s: list[str]
    category: str | None
    published_at: str | None


class ExtractedStructure(TypedDict):
    """Shape returned by `extract_h2s_and_structure` — one SERP competitor."""

    title: str
    snippet: str
    h2s: list[str]
    word_count: int
    has_schema: bool
    schema_types: list[str]
    internal_link_count: int
    external_link_count: int


def extract_content(html: str) -> ExtractedPost:
    """Return title, main text, word count, H2 list, category, published date."""
    main_text = (
        trafilatura.extract(html, include_comments=False, include_tables=False, favor_recall=True)
        or ""
    )

    tree = HTMLParser(html)

    title = _first_text(tree, "h1") or _meta(tree, "og:title") or _title_tag(tree) or ""
    h2s = [n.text(strip=True) for n in tree.css("h2") if n.text(strip=True)]
    category = _category(tree)
    published_at = _published_at(tree)
    word_count = len(re.findall(r"\S+", main_text))

    return {
        "title": title.strip(),
        "main_text": main_text,
        "word_count": word_count,
        "h2s": h2s,
        "category": category,
        "published_at": published_at,
    }


def extract_h2s_and_structure(html: str) -> ExtractedStructure:
    """Extract structural info for SERP competitor analysis."""
    tree = HTMLParser(html)
    h2s = [n.text(strip=True) for n in tree.css("h2") if n.text(strip=True)]
    schema_types = _schema_types(tree)
    title = _first_text(tree, "h1") or _title_tag(tree) or ""
    description = _meta(tree, "description") or _meta(tree, "og:description") or ""

    internal_links, external_links = 0, 0
    for node in tree.css("a[href]"):
        href = (node.attributes.get("href") or "").strip()
        if not href or href.startswith("#") or href.startswith("mailto:"):
            continue
        if href.startswith("http"):
            external_links += 1
        else:
            internal_links += 1

    main_text = trafilatura.extract(html, include_comments=False) or ""
    word_count = len(re.findall(r"\S+", main_text))

    return {
        "title": title,
        "snippet": description,
        "h2s": h2s,
        "word_count": word_count,
        "has_schema": bool(schema_types),
        "schema_types": schema_types,
        "internal_link_count": internal_links,
        "external_link_count": external_links,
    }


def _first_text(tree: HTMLParser, selector: str) -> str | None:
    node = tree.css_first(selector)
    return node.text(strip=True) if node else None


def _title_tag(tree: HTMLParser) -> str | None:
    return _first_text(tree, "title")


def _meta(tree: HTMLParser, key: str) -> str | None:
    for attr in ("property", "name"):
        node = tree.css_first(f'meta[{attr}="{key}"]')
        if node and node.attributes.get("content"):
            return node.attributes["content"].strip()
    return None


def _category(tree: HTMLParser) -> str | None:
    # Try breadcrumbs, then meta tags
    crumb = tree.css_first('[itemtype*="BreadcrumbList"] [itemprop="name"]')
    if crumb and crumb.text(strip=True):
        return crumb.text(strip=True)
    meta_cat = _meta(tree, "article:section") or _meta(tree, "category")
    return meta_cat


def _published_at(tree: HTMLParser) -> str | None:
    candidates = (
        _meta(tree, "article:published_time"),
        _meta(tree, "og:published_time"),
        _meta(tree, "date"),
    )
    for c in candidates:
        if c:
            return c
    time_node = tree.css_first("time[datetime]")
    if time_node:
        return time_node.attributes.get("datetime")
    return None


def _schema_types(tree: HTMLParser) -> list[str]:
    types: list[str] = []
    for node in tree.css('script[type="application/ld+json"]'):
        raw = node.text() or ""
        try:
            data = json.loads(raw)
        except (ValueError, json.JSONDecodeError):
            continue
        types.extend(_collect_types(data))
    # dedupe preserving order
    seen: set[str] = set()
    out: list[str] = []
    for t in types:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _collect_types(data: Any) -> list[str]:
    out: list[str] = []
    if isinstance(data, dict):
        t = data.get("@type")
        if isinstance(t, str):
            out.append(t)
        elif isinstance(t, list):
            out.extend([x for x in t if isinstance(x, str)])
        for v in data.values():
            out.extend(_collect_types(v))
    elif isinstance(data, list):
        for item in data:
            out.extend(_collect_types(item))
    return out
