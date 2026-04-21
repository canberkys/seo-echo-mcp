"""Smoke tests for detect_content_gaps and check_duplicates."""

from __future__ import annotations

import pytest

from seo_echo_mcp.schemas import (
    CompetitorAnalysis,
    CompetitorInsights,
    PostSample,
    SerpEntry,
)
from seo_echo_mcp.tools.check_duplicates import check_duplicates
from seo_echo_mcp.tools.detect_content_gaps import detect_content_gaps


def _serp_entry(url: str, title: str, h2s: list[str], position: int) -> SerpEntry:
    return SerpEntry(
        url=url,
        title=title,
        position=position,
        snippet="",
        h2s=h2s,
        word_count=1500,
        has_schema=False,
        schema_types=[],
        internal_link_count=3,
        external_link_count=3,
    )


def _competitor_analysis(
    entries: list[SerpEntry], keyword: str = "kubernetes"
) -> CompetitorAnalysis:
    return CompetitorAnalysis(
        keyword=keyword,
        language="en",
        country="us",
        fetched_at="2026-04-21T00:00:00+00:00",
        results=entries,
        insights=CompetitorInsights(
            average_word_count=1500,
            word_count_range=(1000, 2000),
            common_h2_topics=[],
            dominant_format="guide",
            title_patterns=[],
            schema_adoption_pct=0.5,
            avg_internal_links=3,
            avg_external_links=3,
        ),
    )


@pytest.mark.asyncio
async def test_detect_content_gaps_surfaces_missing_topics(site_profile_en):
    entries = [
        _serp_entry(
            "https://a.test/1",
            "Kubernetes Ingress Patterns",
            ["Ingress controllers", "TLS termination"],
            1,
        ),
        _serp_entry(
            "https://b.test/2",
            "Service Mesh for Kubernetes",
            ["Ingress controllers", "Istio setup"],
            2,
        ),
    ]
    report = await detect_content_gaps(site_profile_en, _competitor_analysis(entries))
    topics = {g.topic for g in report.gaps}
    assert "ingress" in topics or "controllers" in topics
    assert all(g.coverage_count >= 2 for g in report.gaps)


@pytest.mark.asyncio
async def test_check_duplicates_flags_overlapping_post(site_profile_en):
    site_profile_en.existing_posts = [
        PostSample(
            url="https://example.test/posts/existing-kubernetes-guide",
            title="The Complete Kubernetes Guide",
            h2s=[],
            word_count=2000,
            category="Guides",
            snippet="A complete guide to Kubernetes cluster management and deployment.",
        ),
    ]
    report = await check_duplicates("kubernetes cluster management", site_profile_en)
    assert len(report.matches) == 1
    assert report.matches[0].overlap_score > 0.3
    assert report.verdict in ("caution", "duplicate")


@pytest.mark.asyncio
async def test_check_duplicates_safe_when_no_overlap(site_profile_en):
    site_profile_en.existing_posts = [
        PostSample(
            url="https://example.test/posts/completely-different",
            title="Why coffee beats tea",
            h2s=[],
            word_count=800,
            category="Opinion",
            snippet="A hot take on the coffee versus tea debate.",
        ),
    ]
    report = await check_duplicates("kubernetes ingress", site_profile_en)
    assert report.verdict == "safe"
    assert report.matches == []
