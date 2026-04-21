"""analyze_site: crawl a blog and extract its profile + voice."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx
import py3langid

from seo_echo_mcp import __version__
from seo_echo_mcp.extractors.content import extract_content
from seo_echo_mcp.extractors.sitemap import discover_posts
from seo_echo_mcp.extractors.style import analyze_style
from seo_echo_mcp.schemas import PostSample, SiteProfile

logger = logging.getLogger(__name__)

_USER_AGENT = f"seo-echo-mcp/{__version__} (+https://github.com/canberkys/seo-echo-mcp)"
_MAX_CONCURRENCY = 5
_DEFAULT_CACHE_TTL = 24 * 60 * 60  # 24 hours
_CACHE_DIR = Path(os.environ.get("SEO_ECHO_CACHE_DIR", Path.home() / ".cache" / "seo-echo-mcp"))


async def analyze_site(
    url: str | None = None,
    urls: list[str] | None = None,
    max_samples: int = 12,
    cache_ttl: int = _DEFAULT_CACHE_TTL,
    bypass_cache: bool = False,
) -> SiteProfile:
    """Crawl a blog and produce a SiteProfile summarizing its voice and topics.

    Provide either a root `url` (standard flow — sitemap/feed discovery runs),
    or an explicit `urls` list (skip discovery; useful for JS-rendered sites,
    paywalled blogs, or sites with no/blocked sitemap).

    Args:
        url: Root URL of the blog. Protocol auto-prepended if missing.
        urls: Explicit list of post URLs. If given, sitemap discovery is skipped.
            Domain is inferred from the first URL.
        max_samples: Max posts to sample when discovering via `url` (default 12).
            Ignored when `urls` is provided — all URLs are used.
        cache_ttl: Seconds a cached profile is considered fresh (default 86400 = 24h).
            Set to 0 to disable caching entirely for this call.
        bypass_cache: Force a re-crawl even if a fresh cached profile exists.

    Returns:
        SiteProfile with language, categories, topics, style, and post samples.

    Raises:
        ValueError: When neither `url` nor `urls` is provided, the root URL is
            unreachable, no posts are discoverable, or all fetched pages fail
            content extraction (e.g. JS-rendered sites).
    """
    if not url and not urls:
        raise ValueError("Either `url` or `urls` must be provided.")

    if url:
        root = _normalize_url(url)
        domain = urlparse(root).netloc
    else:
        # urls-only mode — infer domain from the first URL
        first = urls[0]
        if not first.startswith(("http://", "https://")):
            first = "https://" + first
        parsed = urlparse(first)
        domain = parsed.netloc
        root = f"{parsed.scheme}://{domain}"

    cache_key = domain
    if not bypass_cache and cache_ttl > 0:
        cached = _read_cache(cache_key, cache_ttl)
        if cached is not None:
            logger.info("analyze_site cache hit domain=%s", cache_key)
            return cached

    logger.info(
        "analyze_site start url=%s urls=%d max_samples=%d",
        root,
        len(urls) if urls else 0,
        max_samples,
    )

    async with httpx.AsyncClient(
        headers={"User-Agent": _USER_AGENT},
        follow_redirects=True,
        timeout=httpx.Timeout(15.0, connect=10.0),
    ) as client:
        if urls:
            # Skip reachability + sitemap — caller vouches for the URLs.
            candidate_urls = [u if u.startswith("http") else "https://" + u for u in urls]
            logger.info("analyze_site urls-mode count=%d", len(candidate_urls))
        else:
            try:
                await client.head(root, timeout=10.0)
            except httpx.HTTPError as e:
                logger.warning("analyze_site unreachable url=%s err=%s", root, e)
                raise ValueError(f"Unable to reach URL: {root}") from e

            candidate_urls = await discover_posts(root, client)
            logger.info("analyze_site discovered=%d candidate URLs", len(candidate_urls))
            if not candidate_urls:
                raise ValueError(
                    f"Could not discover any posts for {root}. "
                    "Pass a list via the `urls` parameter to skip sitemap discovery."
                )

        selected = candidate_urls if urls else _select_samples(candidate_urls, max_samples)
        fetched = await _fetch_many(selected, client)

    posts: list[PostSample] = []
    bodies: list[str] = []
    h2_lists: list[list[str]] = []
    categories: list[str] = []

    for post_url, html in fetched:
        if not html:
            continue
        data = extract_content(html)
        if not data["main_text"]:
            continue
        posts.append(
            PostSample(
                url=post_url,
                title=data["title"],
                h2s=data["h2s"],
                word_count=data["word_count"],
                category=data["category"],
                snippet=data["main_text"][:200],
                published_at=data["published_at"],
            )
        )
        bodies.append(data["main_text"])
        h2_lists.append(data["h2s"])
        if data["category"]:
            categories.append(data["category"])

    if not posts:
        raise ValueError(
            "Posts found but content extraction failed. "
            "Site may be JS-rendered or block automated fetches."
        )

    combined = "\n\n".join(bodies)
    language, confidence = _detect_language(combined, bodies)
    style = analyze_style(bodies, h2_lists, language)
    topics = _top_tokens(combined, language, n=8)
    top_cats = [c for c, _ in Counter(categories).most_common(5)]
    logger.info(
        "analyze_site done url=%s lang=%s (%s) posts=%d tone=%s h2_pattern=%s",
        root,
        language,
        confidence,
        len(posts),
        style.tone,
        style.h2_pattern,
    )

    profile = SiteProfile(
        domain=domain,
        url=root,
        language=language,
        language_confidence=confidence,
        sampled_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        sample_count=len(posts),
        sample_urls=[p.url for p in posts],
        categories=top_cats,
        topics=topics,
        style=style,
        existing_posts=posts,
    )

    if cache_ttl > 0:
        _write_cache(cache_key, profile)

    return profile


def _read_cache(cache_key: str, ttl: int) -> SiteProfile | None:
    path = _CACHE_DIR / f"{cache_key}.json"
    if not path.exists():
        return None
    try:
        age = time.time() - path.stat().st_mtime
        if age > ttl:
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return SiteProfile.model_validate(data)
    except (OSError, ValueError) as e:
        logger.debug("cache read failed key=%s err=%s", cache_key, e)
        return None


def _write_cache(cache_key: str, profile: SiteProfile) -> None:
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path = _CACHE_DIR / f"{cache_key}.json"
        path.write_text(profile.model_dump_json(indent=2), encoding="utf-8")
        logger.debug("cache write key=%s path=%s", cache_key, path)
    except OSError as e:
        logger.debug("cache write failed key=%s err=%s", cache_key, e)


def _normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


def _select_samples(urls: list[str], k: int) -> list[str]:
    if len(urls) <= k:
        return urls
    # Simple deterministic sampling: take first k/2 + last k/2 to cover
    # recent + older-but-indexed posts (sitemap ordering is typically by date).
    head = urls[: k // 2]
    tail = urls[-(k - len(head)) :]
    return head + tail


async def _fetch_many(urls: list[str], client: httpx.AsyncClient) -> list[tuple[str, str | None]]:
    sem = asyncio.Semaphore(_MAX_CONCURRENCY)

    async def _one(u: str) -> tuple[str, str | None]:
        async with sem:
            try:
                r = await client.get(u, timeout=15.0)
            except httpx.HTTPError:
                return (u, None)
            if r.status_code != 200:
                return (u, None)
            return (u, r.text)

    return await asyncio.gather(*[_one(u) for u in urls])


def _detect_language(combined: str, bodies: list[str]) -> tuple[str, str]:
    if not combined.strip():
        return ("en", "mixed")
    lang, _ = py3langid.classify(combined)
    if not bodies:
        return (lang, "medium")
    per_post_langs = [py3langid.classify(b)[0] for b in bodies if b.strip()]
    if not per_post_langs:
        return (lang, "medium")
    counts = Counter(per_post_langs)
    top_lang, top_count = counts.most_common(1)[0]
    ratio = top_count / len(per_post_langs)
    if ratio >= 0.9:
        confidence = "high"
    elif ratio >= 0.7:
        confidence = "medium"
    else:
        confidence = "mixed"
    return (top_lang, confidence)


def _top_tokens(text: str, language: str, n: int) -> list[str]:
    tokens = re.findall(r"[\w]{4,}", text.lower())
    stop = _STOPWORDS.get(language, _STOPWORDS["en"])
    filtered = [t for t in tokens if t not in stop]
    counts = Counter(filtered)
    return [t for t, _ in counts.most_common(n)]


_STOPWORDS: dict[str, set[str]] = {
    "en": {
        "this",
        "that",
        "with",
        "from",
        "have",
        "will",
        "your",
        "about",
        "which",
        "been",
        "they",
        "their",
        "there",
        "what",
        "when",
        "more",
        "than",
        "some",
        "these",
        "would",
        "could",
        "should",
        "into",
        "because",
    },
    "tr": {
        "için",
        "daha",
        "ancak",
        "veya",
        "ile",
        "bir",
        "bu",
        "şu",
        "olarak",
        "olduğu",
        "gibi",
        "kadar",
        "hem",
        "çok",
        "sonra",
        "önce",
        "yani",
    },
    "es": {
        "para",
        "porque",
        "como",
        "pero",
        "cuando",
        "donde",
        "este",
        "esta",
        "esos",
        "todos",
        "entre",
        "sobre",
        "hasta",
        "desde",
    },
    "fr": {
        "pour",
        "avec",
        "mais",
        "quand",
        "cette",
        "comme",
        "entre",
        "dans",
        "leur",
        "leurs",
        "sans",
        "après",
        "avant",
    },
    "de": {
        "und",
        "oder",
        "aber",
        "wenn",
        "wie",
        "mit",
        "ohne",
        "zwischen",
        "dieser",
        "diese",
        "dieses",
        "jener",
        "bevor",
        "nachdem",
    },
}
