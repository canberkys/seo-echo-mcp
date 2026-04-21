"""Smoke tests for prepare_draft_skeleton."""

from __future__ import annotations

import pytest

from seo_echo_mcp.tools.generate_faq_section import generate_faq_section
from seo_echo_mcp.tools.generate_outline import generate_outline
from seo_echo_mcp.tools.generate_schema_jsonld import generate_schema_jsonld
from seo_echo_mcp.tools.prepare_draft_skeleton import prepare_draft_skeleton


@pytest.mark.asyncio
async def test_draft_skeleton_basic(site_profile_en):
    outline = await generate_outline("kubernetes ingress", site_profile_en)
    skeleton = await prepare_draft_skeleton(outline, site_profile_en)
    assert skeleton.language == "en"
    assert skeleton.slug
    assert skeleton.frontmatter["keyword"] == "kubernetes ingress"
    md = skeleton.markdown
    assert md.startswith("---\n")
    assert "<!-- WRITE intro" in md
    assert md.count("<!-- WRITE section") >= 3
    assert "<!-- CTA:" in md


@pytest.mark.asyncio
async def test_draft_skeleton_turkish_never_em_dash_directive(site_profile_tr):
    outline = await generate_outline("vmware snapshot", site_profile_tr)
    skeleton = await prepare_draft_skeleton(outline, site_profile_tr)
    assert "Do NOT use em-dashes" in skeleton.markdown


@pytest.mark.asyncio
async def test_draft_skeleton_voice_override_forces_never_em_dash(site_profile_en):
    # Simulate a site whose heuristic said 'occasional' — baseline directive is soft.
    site_profile_en.style = site_profile_en.style.model_copy(
        update={"em_dash_frequency": "occasional"}
    )
    outline = await generate_outline("kubernetes ingress", site_profile_en)
    baseline = await prepare_draft_skeleton(outline, site_profile_en)
    assert "Do NOT use em-dashes" not in baseline.markdown

    overridden = await prepare_draft_skeleton(
        outline, site_profile_en, voice_overrides={"em_dash_frequency": "never"}
    )
    assert "Do NOT use em-dashes" in overridden.markdown


@pytest.mark.asyncio
async def test_draft_skeleton_includes_faq_and_schema_when_provided(site_profile_en):
    outline = await generate_outline("kubernetes ingress", site_profile_en)
    faq = await generate_faq_section("kubernetes ingress", language="en")
    schema = await generate_schema_jsonld(
        schema_type="Article",
        title="Kubernetes Ingress",
        description="Guide.",
        url="https://ex.test/p",
        author_name="Author",
        published_at="2026-04-21",
    )
    skeleton = await prepare_draft_skeleton(outline, site_profile_en, faq_section=faq, schema_jsonld=schema)
    assert skeleton.has_faq is True
    assert skeleton.has_schema is True
    assert "Frequently Asked Questions" in skeleton.markdown
    assert "FAQPage" in skeleton.markdown
    assert '"@type": "Article"' in skeleton.markdown
