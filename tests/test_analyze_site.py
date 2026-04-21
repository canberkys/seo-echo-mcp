"""Smoke tests for analyze_site with mocked HTTP."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import respx

from seo_echo_mcp.tools.analyze_site import analyze_site

FIXTURES = Path(__file__).parent / "fixtures"


POST_HTML = """<!doctype html>
<html lang="en">
<head><title>First Post</title>
<meta property="article:published_time" content="2026-03-01T10:00:00+00:00" />
<meta property="article:section" content="Guides" />
</head>
<body>
<h1>First Post</h1>
<article>
<p>This is a long introduction paragraph about testing in Python. It has many
sentences to meet the word count floor. Testing helps you ship software with
confidence. You write tests, you run tests, you refactor safely.</p>
<h2>Why testing matters</h2>
<p>When you skip tests, regressions creep in. You should care about coverage.
This post shows you how we approach unit tests in our projects.</p>
<h2>Our testing stack</h2>
<p>We use pytest, respx for HTTP mocking, and ruff for linting. Our CI runs
on GitHub Actions across multiple Python versions.</p>
</article>
</body></html>"""


@pytest.mark.asyncio
async def test_analyze_site_happy_path():
    sitemap = (FIXTURES / "sample_sitemap.xml").read_text()
    with respx.mock(assert_all_called=False) as mock:
        mock.head("https://example.test").respond(200)
        mock.get("https://example.test/sitemap.xml").respond(200, text=sitemap)
        mock.get("https://example.test/posts/first-post").respond(200, text=POST_HTML)
        mock.get("https://example.test/posts/second-post").respond(200, text=POST_HTML)
        mock.get("https://example.test/posts/third-post").respond(200, text=POST_HTML)

        profile = await analyze_site("example.test", max_samples=3, bypass_cache=True, cache_ttl=0)

    assert profile.domain == "example.test"
    assert profile.language == "en"
    assert profile.sample_count == 3
    assert profile.style.tone
    assert profile.style.h2_pattern in ("question", "statement", "imperative", "mixed")
    assert profile.existing_posts[0].title == "First Post"


@pytest.mark.asyncio
async def test_analyze_site_raises_on_unreachable():
    with respx.mock(assert_all_called=False) as mock:
        mock.head("https://nowhere.invalid").mock(side_effect=httpx.ConnectError("no route"))
        with pytest.raises(ValueError, match="Unable to reach"):
            await analyze_site("nowhere.invalid", bypass_cache=True, cache_ttl=0)


@pytest.mark.asyncio
async def test_analyze_site_raises_when_no_posts_discovered():
    with respx.mock(assert_all_called=False) as mock:
        mock.head("https://empty.test").respond(200)
        mock.get(host="empty.test").respond(404)
        with pytest.raises(ValueError, match="Could not discover"):
            await analyze_site("empty.test", bypass_cache=True, cache_ttl=0)
