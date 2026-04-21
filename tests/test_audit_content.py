"""Smoke tests for audit_content."""

from __future__ import annotations

import pytest

from seo_echo_mcp.tools.audit_content import audit_content


@pytest.mark.asyncio
async def test_audit_flags_em_dash_when_profile_says_never(site_profile_en):
    draft = """# My Post

This is an intro — with a forbidden em dash.

## Section

Body text here."""
    report = await audit_content(draft, site_profile_en)
    em_dash = next(c for c in report.checks if c.name == "em_dash_usage")
    assert em_dash.pass_ is False
    assert em_dash.severity == "error"


@pytest.mark.asyncio
async def test_audit_catches_ai_cliches_in_turkish(site_profile_tr):
    draft = """# Başlık

Günümüz dünyasında yapay zeka çok önemlidir. Sonuç olarak herkes kullanıyor.

## Gövde

Bu bir örnek paragraftır. İçerik kısa tutuldu."""
    report = await audit_content(draft, site_profile_tr)
    cliche = next(c for c in report.checks if c.name == "ai_cliches")
    assert cliche.pass_ is False
    assert cliche.severity == "warning"


@pytest.mark.asyncio
async def test_audit_score_deducts_for_failures(site_profile_en):
    draft = """# Short

Tiny body — with em dash."""
    report = await audit_content(draft, site_profile_en)
    assert 0 <= report.overall_score < 100
    assert report.reading_time_minutes >= 1
    assert report.detected_language


@pytest.mark.asyncio
async def test_audit_meta_description_length(site_profile_en):
    draft = "# Title\n\nHello world."
    short_meta = "Too short."
    report = await audit_content(draft, site_profile_en, target_meta_description=short_meta)
    meta_check = next(c for c in report.checks if c.name == "meta_description_length")
    assert meta_check.pass_ is False


@pytest.mark.asyncio
async def test_audit_keyword_in_title(site_profile_en):
    draft = "# A Generic Title\n\nFastMCP is a thing.\n\n## Section\n\nBody."
    report = await audit_content(draft, site_profile_en, target_keyword="fastmcp")
    title_check = next(c for c in report.checks if c.name == "keyword_in_title")
    assert title_check.pass_ is False


@pytest.mark.asyncio
async def test_voice_overrides_escalate_em_dash_to_error(site_profile_en):
    # Site profile default is em_dash_frequency='never' in the fixture, but let's
    # simulate a real site where the heuristic measured 'occasional'.
    site_profile_en.style = site_profile_en.style.model_copy(
        update={"em_dash_frequency": "occasional"}
    )
    draft = "# Post\n\nIntro — with em dash.\n\n## Section\n\nBody."
    # Without override: occasional is permissive, no em-dash error.
    report_default = await audit_content(draft, site_profile_en)
    em_default = next(c for c in report_default.checks if c.name == "em_dash_usage")
    assert em_default.pass_ is True
    # With override: forcing 'never' turns any em-dash into an error.
    report_override = await audit_content(
        draft, site_profile_en, voice_overrides={"em_dash_frequency": "never"}
    )
    em_override = next(c for c in report_override.checks if c.name == "em_dash_usage")
    assert em_override.pass_ is False
    assert em_override.severity == "error"
