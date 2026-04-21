"""SERP discovery: DuckDuckGo HTML primary, Bing HTML fallback, Google CSE opt-in.

DuckDuckGo's HTML endpoint rate-limits aggressively; when it returns 202/429
or an empty result set, we transparently fall back to Bing's HTML endpoint.
If the user sets GOOGLE_CSE_API_KEY + GOOGLE_CSE_ID, we prefer that path.
"""

from __future__ import annotations

import os
from urllib.parse import quote_plus, urlparse

import httpx
from selectolax.parser import HTMLParser


class SerpError(RuntimeError):
    """Raised when every SERP provider fails."""


async def search(
    query: str,
    language: str,
    country: str,
    top_n: int,
    client: httpx.AsyncClient,
) -> list[dict[str, str]]:
    """Return up to `top_n` SERP entries as dicts with keys: url, title, snippet, position."""
    cse_key = os.environ.get("GOOGLE_CSE_API_KEY")
    cse_id = os.environ.get("GOOGLE_CSE_ID")
    if cse_key and cse_id:
        try:
            results = await _google_cse(query, language, country, top_n, cse_key, cse_id, client)
            if results:
                return results
        except httpx.HTTPError:
            pass

    try:
        results = await _duckduckgo(query, language, country, top_n, client)
        if results:
            return results
    except httpx.HTTPError:
        pass

    try:
        results = await _bing(query, language, country, top_n, client)
        if results:
            return results
    except httpx.HTTPError as e:
        raise SerpError(f"All SERP providers failed: {e}") from e

    raise SerpError("No SERP results found via DuckDuckGo or Bing.")


async def _duckduckgo(
    query: str, language: str, country: str, top_n: int, client: httpx.AsyncClient
) -> list[dict[str, str]]:
    kl = f"{country.lower()}-{language.lower()}"
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}&kl={kl}"
    r = await client.get(url, timeout=20.0, headers={"Accept-Language": language})
    if r.status_code != 200 or not r.text:
        return []
    tree = HTMLParser(r.text)
    results: list[dict[str, str]] = []
    for i, node in enumerate(tree.css("a.result__a"), start=1):
        href = node.attributes.get("href") or ""
        # DDG wraps targets in a redirect sometimes: /l/?uddg=<encoded>
        href = _strip_ddg_redirect(href)
        title = node.text(strip=True)
        snippet_node = node.parent.parent.css_first(".result__snippet") if node.parent else None
        snippet = snippet_node.text(strip=True) if snippet_node else ""
        if href and title:
            results.append({"url": href, "title": title, "snippet": snippet, "position": str(i)})
        if len(results) >= top_n:
            break
    return results


async def _bing(
    query: str, language: str, country: str, top_n: int, client: httpx.AsyncClient
) -> list[dict[str, str]]:
    url = f"https://www.bing.com/search?q={quote_plus(query)}&setlang={language}&cc={country}"
    r = await client.get(
        url,
        timeout=20.0,
        headers={
            "Accept-Language": f"{language},en;q=0.8",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            ),
        },
    )
    if r.status_code != 200 or not r.text:
        return []
    tree = HTMLParser(r.text)
    results: list[dict[str, str]] = []
    for i, item in enumerate(tree.css("li.b_algo"), start=1):
        h2 = item.css_first("h2 a")
        if not h2:
            continue
        href = h2.attributes.get("href") or ""
        title = h2.text(strip=True)
        snippet_node = item.css_first(".b_caption p") or item.css_first("p")
        snippet = snippet_node.text(strip=True) if snippet_node else ""
        if href and title:
            results.append({"url": href, "title": title, "snippet": snippet, "position": str(i)})
        if len(results) >= top_n:
            break
    return results


async def _google_cse(
    query: str,
    language: str,
    country: str,
    top_n: int,
    api_key: str,
    cse_id: str,
    client: httpx.AsyncClient,
) -> list[dict[str, str]]:
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
        "num": min(top_n, 10),
        "hl": language,
        "gl": country,
    }
    r = await client.get(url, params=params, timeout=20.0)
    if r.status_code != 200:
        return []
    data = r.json()
    items = data.get("items") or []
    return [
        {
            "url": it.get("link", ""),
            "title": it.get("title", ""),
            "snippet": it.get("snippet", ""),
            "position": str(i),
        }
        for i, it in enumerate(items, start=1)
    ]


def _strip_ddg_redirect(href: str) -> str:
    if href.startswith("//duckduckgo.com/l/") or href.startswith("/l/"):
        parsed = urlparse("https:" + href if href.startswith("//") else "https://duckduckgo.com" + href)
        qs = dict(p.split("=", 1) for p in parsed.query.split("&") if "=" in p)
        from urllib.parse import unquote

        if "uddg" in qs:
            return unquote(qs["uddg"])
    return href
