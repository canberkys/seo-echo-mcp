"""Smoke tests for analyze_internal_links."""

from __future__ import annotations

import pytest

from seo_echo_mcp.schemas import PostSample
from seo_echo_mcp.tools.analyze_internal_links import analyze_internal_links

_DRAFT_WITH_LINKS = """# Kubernetes Guide

Learn how to manage your Kubernetes cluster effectively.

## Setting Up

First, install kubectl. See also [our cluster setup post](https://example.test/posts/cluster-setup).

## Networking

Configure [ingress controllers](https://example.test/posts/ingress-guide) for routing.
External reference: [official docs](https://kubernetes.io/docs).

## Monitoring

Use Prometheus. No links here yet.
"""

_DRAFT_NO_LINKS = """# Plain Post

This post has no links at all.

## Section One

Just text.

## Section Two

More text.
"""


@pytest.mark.asyncio
async def test_counts_internal_and_external(site_profile_en):
    site_profile_en.existing_posts = [
        PostSample(
            url="https://example.test/posts/cluster-setup",
            title="Cluster Setup Guide",
            h2s=["Installation", "Configuration"],
            word_count=1200,
            snippet="How to set up a Kubernetes cluster.",
        ),
        PostSample(
            url="https://example.test/posts/ingress-guide",
            title="Kubernetes Ingress Controllers",
            h2s=["Nginx", "Traefik"],
            word_count=900,
            snippet="Guide to ingress controllers in Kubernetes.",
        ),
    ]
    report = await analyze_internal_links(_DRAFT_WITH_LINKS, site_profile_en)
    assert report.internal_links == 2
    assert report.external_links == 1
    assert report.total_links == 3
    assert "https://example.test/posts/cluster-setup" in report.linked_post_urls
    assert "https://example.test/posts/ingress-guide" in report.linked_post_urls


@pytest.mark.asyncio
async def test_sections_without_links_detected(site_profile_en):
    report = await analyze_internal_links(_DRAFT_WITH_LINKS, site_profile_en)
    # "Monitoring" section has no links
    assert "Monitoring" in report.sections_without_links


@pytest.mark.asyncio
async def test_all_sections_bare_when_no_links(site_profile_en):
    report = await analyze_internal_links(_DRAFT_NO_LINKS, site_profile_en)
    assert report.internal_links == 0
    assert report.external_links == 0
    assert "Section One" in report.sections_without_links
    assert "Section Two" in report.sections_without_links


@pytest.mark.asyncio
async def test_low_density_score_when_no_links(site_profile_en):
    report = await analyze_internal_links(_DRAFT_NO_LINKS, site_profile_en)
    assert report.link_density_score < 50


@pytest.mark.asyncio
async def test_recommendations_present_when_no_links(site_profile_en):
    report = await analyze_internal_links(_DRAFT_NO_LINKS, site_profile_en)
    assert len(report.recommendations) > 0
    assert any("internal" in r.lower() for r in report.recommendations)


@pytest.mark.asyncio
async def test_unlinked_opportunities_by_token_overlap(site_profile_en):
    site_profile_en.existing_posts = [
        PostSample(
            url="https://example.test/posts/monitoring-guide",
            title="Kubernetes Monitoring with Prometheus",
            h2s=["Prometheus setup", "Alerting"],
            word_count=1100,
            snippet="How to monitor Kubernetes with Prometheus.",
        ),
    ]
    # Draft mentions Prometheus + Kubernetes but doesn't link the monitoring post.
    report = await analyze_internal_links(_DRAFT_WITH_LINKS, site_profile_en)
    opp_urls = [o.existing_url for o in report.unlinked_opportunities]
    assert "https://example.test/posts/monitoring-guide" in opp_urls


@pytest.mark.asyncio
async def test_empty_draft_raises(site_profile_en):
    with pytest.raises(ValueError):
        await analyze_internal_links("", site_profile_en)
