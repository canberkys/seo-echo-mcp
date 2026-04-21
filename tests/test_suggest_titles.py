"""Smoke tests for suggest_titles."""

from __future__ import annotations

import pytest

from seo_echo_mcp.tools.suggest_titles import suggest_titles


@pytest.mark.asyncio
async def test_suggest_titles_english_returns_ten(site_profile_en):
    result = await suggest_titles("kubernetes ingress", site_profile_en, count=10)
    assert len(result.items) == 10
    assert result.language == "en"
    assert result.primary_recommendation == result.items[0].title


@pytest.mark.asyncio
async def test_suggest_titles_question_pattern_first_for_question_site(site_profile_tr):
    result = await suggest_titles("vmware snapshot", site_profile_tr, count=5)
    # site_profile_tr has h2_pattern='question' → question variants rank first
    assert result.items[0].pattern == "question"
    assert result.items[0].matches_site_style is True


@pytest.mark.asyncio
async def test_suggest_titles_flags_serp_unsafe_long_titles(site_profile_en):
    # craft a long keyword to force some titles past 60 chars
    result = await suggest_titles(
        "the ultimate guide to distributed consensus algorithms",
        site_profile_en,
        count=5,
    )
    any_unsafe = any(not item.serp_safe for item in result.items)
    assert any_unsafe, "expected at least one long title to exceed 60 chars"


@pytest.mark.asyncio
async def test_suggest_titles_uses_competitor_listicle_n(site_profile_en):
    """When competitors use 'Top 10 ...' / '15 best ...', our listicles should match."""
    from seo_echo_mcp.schemas import CompetitorAnalysis, CompetitorInsights, SerpEntry

    def _entry(title: str, pos: int) -> SerpEntry:
        return SerpEntry(
            url=f"https://x.test/{pos}",
            title=title,
            position=pos,
            snippet="",
            h2s=[],
            word_count=1000,
            has_schema=False,
            schema_types=[],
            internal_link_count=0,
            external_link_count=0,
        )

    competitors = CompetitorAnalysis(
        keyword="kubernetes",
        language="en",
        country="us",
        fetched_at="2026-04-21T00:00:00+00:00",
        results=[
            _entry("10 Best Kubernetes Tips", 1),
            _entry("10 Ways to Use Kubernetes", 2),
            _entry("Top 10 Kubernetes Patterns", 3),
        ],
        insights=CompetitorInsights(
            average_word_count=1000,
            word_count_range=(500, 1500),
            common_h2_topics=[],
            dominant_format="listicle",
            title_patterns=[],
            schema_adoption_pct=0.0,
            avg_internal_links=0,
            avg_external_links=0,
        ),
    )
    result = await suggest_titles("kubernetes", site_profile_en, competitors, count=10)
    listicle_titles = [t.title for t in result.items if t.pattern == "listicle"]
    assert any("10" in t for t in listicle_titles), f"Expected N=10, got: {listicle_titles}"


@pytest.mark.asyncio
async def test_suggest_titles_preserves_keyword_casing(site_profile_en):
    result = await suggest_titles("VMware vMotion", site_profile_en, count=5)
    joined = " ".join(t.title for t in result.items)
    assert "VMware vMotion" in joined
    assert "Vmware Vmotion" not in joined
