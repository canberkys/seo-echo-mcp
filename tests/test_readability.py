"""Smoke tests for readability_report."""

from __future__ import annotations

import pytest

from seo_echo_mcp.tools.readability_report import readability_report


@pytest.mark.asyncio
async def test_readability_english_easy_short_sentences():
    draft = "# Title\n\nThis is fun. Cats are nice. Dogs run fast. We like them all."
    report = await readability_report(draft, language="en")
    assert report.formula_used == "flesch-en"
    assert report.verdict in ("easy", "medium")
    assert report.avg_sentence_words > 0
    assert report.passive_voice_ratio is not None


@pytest.mark.asyncio
async def test_readability_english_hard_long_sentences():
    draft = (
        "# Title\n\n"
        "The implementation of sophisticated distributed consensus algorithms "
        "requires comprehensive understanding of Byzantine fault tolerance "
        "mechanisms, which fundamentally underpin modern infrastructure."
    )
    report = await readability_report(draft, language="en")
    assert report.formula_used == "flesch-en"
    assert report.avg_sentence_words > 15


@pytest.mark.asyncio
async def test_readability_turkish_uses_atesman():
    draft = (
        "# Başlık\n\nBu kısa bir örnek. Cümleler sade. Okuması kolay. "
        "Türkçe formülü denenir."
    )
    report = await readability_report(draft, language="tr")
    assert report.formula_used == "atesman-tr"
    assert report.passive_voice_ratio is None


@pytest.mark.asyncio
async def test_readability_fallback_formula():
    draft = "# Başlık\n\n" + "Kısa cümle. " * 5
    report = await readability_report(draft, language="pl")
    assert report.formula_used == "generic"
