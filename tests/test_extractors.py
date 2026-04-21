"""Smoke tests for sitemap and content extractors."""

from __future__ import annotations

import httpx
import pytest
import respx

from seo_echo_mcp.extractors.content import extract_content, extract_h2s_and_structure
from seo_echo_mcp.extractors.sitemap import discover_posts


@pytest.mark.asyncio
async def test_discover_posts_reads_flat_sitemap():
    sitemap = """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://x.test/a</loc></url>
  <url><loc>https://x.test/b</loc></url>
</urlset>"""
    with respx.mock() as mock:
        mock.get("https://x.test/sitemap.xml").respond(200, text=sitemap)
        async with httpx.AsyncClient() as client:
            urls = await discover_posts("https://x.test", client)
    assert urls == ["https://x.test/a", "https://x.test/b"]


@pytest.mark.asyncio
async def test_discover_posts_follows_sitemap_index():
    index = """<?xml version="1.0"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://x.test/sitemap-posts.xml</loc></sitemap>
</sitemapindex>"""
    child = """<?xml version="1.0"?>
<urlset><url><loc>https://x.test/p1</loc></url></urlset>"""
    with respx.mock() as mock:
        mock.get("https://x.test/sitemap.xml").respond(200, text=index)
        mock.get("https://x.test/sitemap-posts.xml").respond(200, text=child)
        async with httpx.AsyncClient() as client:
            urls = await discover_posts("https://x.test", client)
    assert urls == ["https://x.test/p1"]


def test_extract_content_basic():
    html = """<html><head><title>Hi</title></head><body>
    <h1>Hi</h1>
    <article><p>Body text here with many words to pass extraction threshold.
    Trafilatura needs meaningful body content to emit a result.</p>
    <h2>Section One</h2><p>More stuff here for the extractor.</p></article>
    </body></html>"""
    data = extract_content(html)
    assert data["title"]
    assert "Section One" in data["h2s"]


def test_extract_structure_counts_links_and_schema():
    html = """<html><body>
    <h1>T</h1>
    <h2>S</h2>
    <p>Read <a href="/internal">here</a> or <a href="https://ext.test">there</a>.</p>
    <script type="application/ld+json">{"@type": "Article"}</script>
    </body></html>"""
    data = extract_h2s_and_structure(html)
    assert data["has_schema"] is True
    assert "Article" in data["schema_types"]
    assert data["internal_link_count"] == 1
    assert data["external_link_count"] == 1
