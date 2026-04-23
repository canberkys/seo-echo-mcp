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


@pytest.mark.asyncio
async def test_outline_sections_have_unique_h2s(site_profile_en):
    """Section H2s should never collide, even when the template pool is short."""
    outline = await generate_outline("kubernetes", site_profile_en, target_word_count=3000)
    h2s = [s.h2 for s in outline.sections]
    assert len(h2s) == len(set(h2s)), f"Duplicate H2s found: {h2s}"


@pytest.mark.asyncio
async def test_outline_preserves_keyword_casing(site_profile_tr):
    """`.title()` would turn 'VMware vMotion' into 'Vmware Vmotion'; we must not."""
    outline = await generate_outline("VMware vMotion", site_profile_tr)
    joined = " ".join(s.h2 for s in outline.sections)
    assert "VMware vMotion" in joined
    assert "Vmware Vmotion" not in joined


@pytest.mark.asyncio
async def test_outline_tr_synthetic_fallbacks_are_turkish(site_profile_tr):
    """Long TR outline must not leak English synthetic H2s ('Advanced X techniques')."""
    # target_word_count=3000 → 12 sections → template pool exhausts → synthetic kicks in.
    outline = await generate_outline("VMware vMotion", site_profile_tr, target_word_count=3000)
    joined = " ".join(s.h2 for s in outline.sections)
    # English synthetic fragments that used to leak through:
    for leaked in ("in practice", "Advanced", "tips and tricks", "in production", "use cases"):
        assert leaked not in joined, f"English synthetic H2 leaked: '{leaked}' in {joined!r}"
    # And must_cover items should be Turkish for TR site.
    intro_must_cover = " ".join(outline.sections[0].must_cover)
    assert "Define" not in intro_must_cover
    assert "Why it matters right now" not in intro_must_cover


@pytest.mark.asyncio
async def test_outline_tr_must_cover_is_turkish(site_profile_tr):
    outline = await generate_outline("docker", site_profile_tr)
    summary_must_cover = " ".join(outline.sections[-1].must_cover)
    assert "Key takeaways" not in summary_must_cover
    assert "Next action" not in summary_must_cover
