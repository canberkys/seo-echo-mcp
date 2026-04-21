"""Shared fixtures and a tiny sample SiteProfile builder."""

from __future__ import annotations

import pytest

from seo_echo_mcp.schemas import SiteProfile, StyleProfile


def _style(**overrides) -> StyleProfile:
    base = {
        "average_word_count": 1200,
        "tone": "conversational",
        "addressing": "you",
        "h2_pattern": "statement",
        "uses_lists": True,
        "uses_code_blocks": False,
        "avg_paragraph_sentences": 3.0,
        "em_dash_frequency": "never",
        "avg_sentence_words": 16.0,
    }
    base.update(overrides)
    return StyleProfile(**base)


@pytest.fixture
def site_profile_en() -> SiteProfile:
    return SiteProfile(
        domain="example.test",
        url="https://example.test",
        language="en",
        language_confidence="high",
        sampled_at="2026-04-21T00:00:00+00:00",
        sample_count=3,
        sample_urls=[
            "https://example.test/posts/first-post",
            "https://example.test/posts/second-post",
            "https://example.test/posts/third-post",
        ],
        categories=["Guides"],
        topics=["testing", "python", "mcp"],
        style=_style(),
        existing_posts=[],
    )


@pytest.fixture
def site_profile_tr() -> SiteProfile:
    return SiteProfile(
        domain="example.test",
        url="https://example.test",
        language="tr",
        language_confidence="high",
        sampled_at="2026-04-21T00:00:00+00:00",
        sample_count=2,
        sample_urls=[
            "https://example.test/yazilar/birinci",
            "https://example.test/yazilar/ikinci",
        ],
        categories=["Rehber"],
        topics=["yazılım", "geliştirme"],
        style=_style(addressing="sen", h2_pattern="question"),
        existing_posts=[],
    )
