"""Smoke tests for generate_slug, generate_meta_variations, generate_schema_jsonld, generate_faq_section."""

from __future__ import annotations

import json

import pytest

from seo_echo_mcp.tools.generate_faq_section import generate_faq_section
from seo_echo_mcp.tools.generate_meta_variations import generate_meta_variations
from seo_echo_mcp.tools.generate_schema_jsonld import generate_schema_jsonld
from seo_echo_mcp.tools.generate_slug import generate_slug


@pytest.mark.asyncio
async def test_slug_turkish_transliteration():
    result = await generate_slug("VMware Snapshot Nedir?", language="tr")
    assert result.primary == "vmware-snapshot-nedir"
    assert result.language == "tr"


@pytest.mark.asyncio
async def test_slug_german_umlaut_doubled():
    result = await generate_slug("Über die Zukunft", language="de")
    assert "ueber" in result.primary


@pytest.mark.asyncio
async def test_slug_strips_stopwords_in_alternative():
    result = await generate_slug("The Complete Guide to Kubernetes", language="en")
    assert result.primary.startswith("the-complete-guide")
    assert any("kubernetes" in alt and "the" not in alt.split("-") for alt in result.alternatives)


@pytest.mark.asyncio
async def test_meta_variations_five_angles():
    variations = await generate_meta_variations("kubernetes", "Kubernetes Basics", language="en")
    assert len(variations.items) == 5
    angles = {v.angle for v in variations.items}
    assert angles == {"problem-solution", "question", "benefit", "curiosity", "action"}
    for v in variations.items:
        assert 140 <= v.length <= 160, f"{v.angle}: {v.length} chars — {v.description!r}"


@pytest.mark.asyncio
async def test_schema_article_jsonld_is_valid_json():
    result = await generate_schema_jsonld(
        schema_type="Article",
        title="Test",
        description="Desc",
        url="https://ex.test/p",
        author_name="Someone",
        published_at="2026-04-21",
        image_url="https://ex.test/img.png",
        keywords=["seo", "mcp"],
    )
    data = json.loads(result.json_ld)
    assert data["@type"] == "Article"
    assert data["keywords"] == "seo, mcp"
    assert "<script" in result.html_snippet


@pytest.mark.asyncio
async def test_faq_section_five_items_with_jsonld():
    faq = await generate_faq_section("vmware snapshot", language="tr", count=5)
    assert len(faq.items) == 5
    assert faq.items[0].position == 1
    assert "## Sıkça Sorulan Sorular" in faq.markdown
    data = json.loads(faq.faq_jsonld)
    assert data["@type"] == "FAQPage"
    assert len(data["mainEntity"]) == 5
