"""Smoke tests for analyze_competitors using direct URL input."""

from __future__ import annotations

import pytest
import respx

from seo_echo_mcp.tools.analyze_competitors import analyze_competitors

COMPETITOR_HTML = """<html><head><title>Best SEO Guide 2026</title></head><body>
<h1>Best SEO Guide 2026</h1>
<meta name="description" content="A full SEO guide for 2026." />
<p>Intro paragraph with enough words to pass extraction heuristics.
Trafilatura requires real body content to emit output reliably.
We add a few more sentences so main text is meaningful.</p>
<h2>What is SEO?</h2>
<h2>How to rank in 2026</h2>
<h2>Common mistakes</h2>
<p>Sample body text about SEO best practices and ranking factors.</p>
<a href="/internal-one">one</a>
<a href="https://external.test/x">two</a>
<script type="application/ld+json">{"@type": "Article"}</script>
</body></html>"""


@pytest.mark.asyncio
async def test_analyze_competitors_via_urls_skips_serp():
    with respx.mock() as mock:
        mock.get("https://a.test/post").respond(200, text=COMPETITOR_HTML)
        mock.get("https://b.test/post").respond(200, text=COMPETITOR_HTML)
        result = await analyze_competitors(
            urls=["https://a.test/post", "https://b.test/post"],
            language="en",
            country="us",
            top_n=10,
        )
    assert len(result.results) == 2
    assert result.insights.schema_adoption_pct == 1.0
    assert result.insights.average_word_count >= 0
    assert result.keyword is None


@pytest.mark.asyncio
async def test_analyze_competitors_requires_input():
    with pytest.raises(ValueError, match="Either"):
        await analyze_competitors()
