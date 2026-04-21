"""analyze_competitors: fetch SERP results and extract structural insights."""

from __future__ import annotations

import asyncio
import logging
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Literal

import httpx

from seo_echo_mcp import __version__
from seo_echo_mcp.extractors.content import extract_h2s_and_structure
from seo_echo_mcp.extractors.serp import SerpError, search
from seo_echo_mcp.schemas import CompetitorAnalysis, CompetitorInsights, SerpEntry

logger = logging.getLogger(__name__)

_USER_AGENT = (
    f"seo-echo-mcp/{__version__} "
    "(Mozilla/5.0 compatible; +https://github.com/canberkys/seo-echo-mcp)"
)
_MAX_CONCURRENCY = 5


async def analyze_competitors(
    keyword: str | None = None,
    urls: list[str] | None = None,
    language: str = "en",
    country: str = "us",
    top_n: int = 10,
) -> CompetitorAnalysis:
    """Analyze top SERP results (or a provided URL list) for a target keyword.

    Exactly one of `keyword` or `urls` must be supplied.

    Args:
        keyword: Target keyword to search on SERP. Required if `urls` is None.
        urls: Predetermined list of competitor URLs. Skips SERP discovery.
        language: ISO 639-1 language code. Affects SERP region.
        country: ISO 3166-1 alpha-2 code. Affects SERP region.
        top_n: Max number of results to analyze.

    Returns:
        CompetitorAnalysis with per-URL structure plus aggregated insights.

    Raises:
        ValueError: If neither keyword nor urls provided.
        RuntimeError: If all SERP providers fail (DuckDuckGo + Bing).
    """
    if not keyword and not urls:
        raise ValueError("Either `keyword` or `urls` must be provided.")
    logger.info(
        "analyze_competitors start keyword=%r urls=%d language=%s country=%s",
        keyword,
        len(urls) if urls else 0,
        language,
        country,
    )

    async with httpx.AsyncClient(
        headers={"User-Agent": _USER_AGENT},
        follow_redirects=True,
        timeout=httpx.Timeout(20.0, connect=10.0),
    ) as client:
        if urls:
            serp_seeds = [
                {"url": u, "title": "", "snippet": "", "position": str(i)}
                for i, u in enumerate(urls[:top_n], start=1)
            ]
        else:
            try:
                serp_seeds = await search(keyword, language, country, top_n, client)
            except SerpError as e:
                logger.warning("analyze_competitors SERP failed keyword=%r err=%s", keyword, e)
                raise RuntimeError(str(e)) from e

        pages = await _fetch_many([s["url"] for s in serp_seeds], client)

    results: list[SerpEntry] = []
    for seed, (url, html) in zip(serp_seeds, pages, strict=False):
        if not html:
            continue
        data = extract_h2s_and_structure(html)
        results.append(
            SerpEntry(
                url=url,
                title=data["title"] or seed.get("title", ""),
                position=int(seed.get("position", len(results) + 1)),
                snippet=data["snippet"] or seed.get("snippet", ""),
                h2s=data["h2s"],
                word_count=data["word_count"],
                has_schema=data["has_schema"],
                schema_types=data["schema_types"],
                internal_link_count=data["internal_link_count"],
                external_link_count=data["external_link_count"],
            )
        )

    insights = _aggregate(results)

    return CompetitorAnalysis(
        keyword=keyword,
        language=language,
        country=country,
        fetched_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        results=results,
        insights=insights,
    )


async def _fetch_many(urls: list[str], client: httpx.AsyncClient) -> list[tuple[str, str | None]]:
    sem = asyncio.Semaphore(_MAX_CONCURRENCY)

    async def _one(u: str) -> tuple[str, str | None]:
        async with sem:
            try:
                r = await client.get(u, timeout=20.0)
            except httpx.HTTPError:
                return (u, None)
            if r.status_code != 200:
                return (u, None)
            return (u, r.text)

    return await asyncio.gather(*[_one(u) for u in urls])


def _aggregate(results: list[SerpEntry]) -> CompetitorInsights:
    if not results:
        return CompetitorInsights(
            average_word_count=0,
            word_count_range=(0, 0),
            common_h2_topics=[],
            dominant_format="mixed",
            title_patterns=[],
            schema_adoption_pct=0.0,
            avg_internal_links=0,
            avg_external_links=0,
        )
    wcs = [r.word_count for r in results if r.word_count]
    avg_wc = int(sum(wcs) / max(len(wcs), 1))
    wc_range = (min(wcs), max(wcs)) if wcs else (0, 0)

    all_h2_tokens = []
    for r in results:
        for h in r.h2s:
            all_h2_tokens.extend(re.findall(r"[\w]{4,}", h.lower()))
    common = [t for t, _ in Counter(all_h2_tokens).most_common(8)]

    dominant = _dominant_format([r.title for r in results] + [h for r in results for h in r.h2s])
    schema_pct = sum(1 for r in results if r.has_schema) / len(results)
    avg_internal = int(sum(r.internal_link_count for r in results) / len(results))
    avg_external = int(sum(r.external_link_count for r in results) / len(results))
    title_patterns = _title_patterns([r.title for r in results if r.title])

    return CompetitorInsights(
        average_word_count=avg_wc,
        word_count_range=wc_range,
        common_h2_topics=common,
        dominant_format=dominant,
        title_patterns=title_patterns,
        schema_adoption_pct=round(schema_pct, 2),
        avg_internal_links=avg_internal,
        avg_external_links=avg_external,
    )


def _dominant_format(
    titles_and_h2s: list[str],
) -> Literal["listicle", "guide", "comparison", "tutorial", "review", "news", "mixed"]:
    joined = " ".join(titles_and_h2s).lower()
    counters = {
        "listicle": len(re.findall(r"\b\d{1,3}\s+(best|top|ways|ideas|reasons|tips)\b", joined)),
        "guide": len(re.findall(r"\b(guide|ultimate|complete|handbook)\b", joined)),
        "tutorial": len(re.findall(r"\b(how to|tutorial|step[- ]by[- ]step|step)\b", joined)),
        "comparison": len(re.findall(r"\b(vs\.?|versus|comparison|compared)\b", joined)),
        "review": len(re.findall(r"\b(review|hands[- ]on|verdict|pros and cons)\b", joined)),
        "news": len(re.findall(r"\b(announces|launches|released|breaking|new)\b", joined)),
    }
    best = max(counters, key=counters.get)
    if counters[best] < 2:
        return "mixed"
    return best  # type: ignore[return-value]


def _title_patterns(titles: list[str]) -> list[str]:
    patterns: list[str] = []
    for t in titles:
        p = re.sub(r"\d+", "N", t)
        p = re.sub(r"\b\d{4}\b", "YEAR", p)
        patterns.append(p)
    return [p for p, _ in Counter(patterns).most_common(5)]
