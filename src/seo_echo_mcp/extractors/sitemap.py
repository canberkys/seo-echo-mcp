"""Discover post URLs for a given blog root.

Tries, in order: sitemap.xml, sitemap_index.xml, wp-sitemap.xml, common feed
endpoints, then falls back to parsing links off the homepage.
"""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

import httpx
from selectolax.parser import HTMLParser

SITEMAP_CANDIDATES = (
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/wp-sitemap.xml",
    "/sitemap-index.xml",
    "/sitemap-posts.xml",
)

FEED_CANDIDATES = (
    "/feed/",
    "/feed",
    "/rss.xml",
    "/atom.xml",
    "/rss",
)


async def discover_posts(root_url: str, client: httpx.AsyncClient, limit: int = 200) -> list[str]:
    """Return candidate post URLs for a blog rooted at `root_url`.

    The returned list is deduplicated and bounded by `limit`.
    """
    root_url = root_url.rstrip("/")

    for path in SITEMAP_CANDIDATES:
        urls = await _try_sitemap(urljoin(root_url + "/", path.lstrip("/")), client)
        if urls:
            return _dedupe(urls)[:limit]

    for path in FEED_CANDIDATES:
        urls = await _try_feed(urljoin(root_url + "/", path.lstrip("/")), client)
        if urls:
            return _dedupe(urls)[:limit]

    urls = await _parse_homepage(root_url, client)
    return _dedupe(urls)[:limit]


async def _try_sitemap(url: str, client: httpx.AsyncClient) -> list[str]:
    try:
        r = await client.get(url, timeout=15.0)
    except httpx.HTTPError:
        return []
    if r.status_code != 200 or not r.text:
        return []
    text = r.text

    # Nested sitemap index: contains <sitemap><loc>...</loc></sitemap>
    if "<sitemapindex" in text:
        child_locs = re.findall(r"<loc>\s*([^<]+)\s*</loc>", text)
        collected: list[str] = []
        for child in child_locs[:20]:
            try:
                cr = await client.get(child.strip(), timeout=15.0)
            except httpx.HTTPError:
                continue
            if cr.status_code == 200:
                collected.extend(re.findall(r"<loc>\s*([^<]+)\s*</loc>", cr.text))
        return [u.strip() for u in collected if u.strip()]

    return [u.strip() for u in re.findall(r"<loc>\s*([^<]+)\s*</loc>", text)]


async def _try_feed(url: str, client: httpx.AsyncClient) -> list[str]:
    try:
        r = await client.get(url, timeout=15.0)
    except httpx.HTTPError:
        return []
    if r.status_code != 200 or not r.text:
        return []
    text = r.text
    # RSS <link>...</link>, Atom <link href="..."/>
    rss = re.findall(r"<link>\s*([^<]+)\s*</link>", text)
    atom = re.findall(r'<link[^>]+href="([^"]+)"', text)
    return [u.strip() for u in (rss + atom) if u.strip()]


async def _parse_homepage(root_url: str, client: httpx.AsyncClient) -> list[str]:
    try:
        r = await client.get(root_url, timeout=15.0)
    except httpx.HTTPError:
        return []
    if r.status_code != 200:
        return []
    tree = HTMLParser(r.text)
    host = urlparse(root_url).netloc
    urls: list[str] = []
    for node in tree.css("a[href]"):
        href = node.attributes.get("href") or ""
        full = urljoin(root_url + "/", href)
        parsed = urlparse(full)
        if parsed.netloc != host:
            continue
        path = parsed.path or "/"
        if path in ("/", ""):
            continue
        if any(path.startswith(p) for p in ("/wp-", "/tag/", "/category/", "/author/", "/page/")):
            continue
        urls.append(full.split("#")[0])
    return urls


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out
