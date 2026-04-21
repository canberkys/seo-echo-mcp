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
