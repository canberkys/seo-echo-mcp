"""Smoke tests for analyze_site `urls` param and cache behavior."""

from __future__ import annotations

import pytest
import respx

from seo_echo_mcp.tools.analyze_site import analyze_site

POST_HTML = """<!doctype html>
<html lang="en">
<head><title>Post</title></head>
<body>
<h1>Post</h1>
<article>
<p>This is a long introduction paragraph about testing in Python. It has many
sentences to meet the word count floor. Testing helps you ship software with
confidence. You write tests, you run tests, you refactor safely.</p>
<h2>Why it matters</h2>
<p>Because regressions creep in otherwise.</p>
</article>
</body></html>"""


@pytest.mark.asyncio
async def test_analyze_site_urls_param_skips_sitemap(tmp_path, monkeypatch):
    monkeypatch.setenv("SEO_ECHO_CACHE_DIR", str(tmp_path))
    # Re-import to pick up the monkeypatched env var in module-level _CACHE_DIR.
    import importlib

    import seo_echo_mcp.tools.analyze_site as mod

    importlib.reload(mod)
    with respx.mock(assert_all_called=False) as mock:
        mock.get("https://direct.test/a").respond(200, text=POST_HTML)
        mock.get("https://direct.test/b").respond(200, text=POST_HTML)
        profile = await mod.analyze_site(
            urls=["https://direct.test/a", "https://direct.test/b"],
            bypass_cache=True,
            cache_ttl=0,
        )
    assert profile.domain == "direct.test"
    assert profile.sample_count == 2


@pytest.mark.asyncio
async def test_analyze_site_requires_url_or_urls():
    with pytest.raises(ValueError, match="Either"):
        await analyze_site(bypass_cache=True, cache_ttl=0)


@pytest.mark.asyncio
async def test_analyze_site_cache_hit_avoids_refetch(tmp_path, monkeypatch):
    monkeypatch.setenv("SEO_ECHO_CACHE_DIR", str(tmp_path))
    import importlib

    import seo_echo_mcp.tools.analyze_site as mod

    importlib.reload(mod)
    with respx.mock(assert_all_called=False) as mock:
        mock.get("https://cached.test/a").respond(200, text=POST_HTML)
        first = await mod.analyze_site(urls=["https://cached.test/a"], cache_ttl=3600)
        # Second call should hit the cache — no new HTTP request needed.
    assert first.sample_count == 1
    assert (tmp_path / "cached.test.json").exists()

    with respx.mock(assert_all_called=False) as _:
        second = await mod.analyze_site(urls=["https://cached.test/a"], cache_ttl=3600)
    assert second.domain == first.domain
    assert second.sampled_at == first.sampled_at  # same cached payload
