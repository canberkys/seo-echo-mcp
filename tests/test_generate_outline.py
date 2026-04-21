"""Smoke tests for generate_outline."""

from __future__ import annotations

import pytest

from seo_echo_mcp.tools.generate_outline import generate_outline


@pytest.mark.asyncio
async def test_outline_english_basic(site_profile_en):
    outline = await generate_outline("machine learning", site_profile_en)
    assert outline.keyword == "machine learning"
    assert outline.language == "en"
    assert len(outline.suggested_titles) == 3
    assert len(outline.suggested_meta_descriptions) == 3
    assert 5 <= len(outline.sections) <= 12
    assert outline.sections[0].purpose == "introduction"
    assert outline.sections[-1].purpose == "summary"


@pytest.mark.asyncio
async def test_outline_turkish_uses_question_pattern(site_profile_tr):
    outline = await generate_outline("yapay zeka", site_profile_tr)
    assert outline.language == "tr"
    assert outline.h2_style == "question"
    # First section H2 should be formatted as a question given profile
    assert outline.sections[0].h2.endswith("?")


@pytest.mark.asyncio
async def test_outline_respects_target_word_count(site_profile_en):
    outline = await generate_outline("seo", site_profile_en, target_word_count=500)
    assert outline.word_count_target == 500
    # 500 / 250 = 2, clamped to minimum 5
    assert len(outline.sections) == 5
