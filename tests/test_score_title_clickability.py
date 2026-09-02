"""Smoke tests for score_title_clickability."""

from __future__ import annotations

import pytest

from seo_echo_mcp.tools.score_title_clickability import score_title_clickability


@pytest.mark.asyncio
async def test_scores_single_title():
    report = await score_title_clickability(
        ["10 Best Kubernetes Tips for 2025"], keyword="kubernetes"
    )
    assert len(report.items) == 1
    item = report.items[0]
    assert item.score > 50
    assert "contains number" in item.signals
    assert "keyword present" in item.signals
    assert item.serp_safe is True


@pytest.mark.asyncio
async def test_top_pick_is_highest_score():
    titles = [
        "Kubernetes",
        "The Ultimate Guide to Kubernetes Cluster Management in 2025",
        "7 Kubernetes Tips That Actually Work",
    ]
    report = await score_title_clickability(titles, keyword="kubernetes")
    scores = {i.title: i.score for i in report.items}
    assert scores[report.top_pick] == max(scores.values())


@pytest.mark.asyncio
async def test_short_title_penalised():
    report = await score_title_clickability(["Kubernetes"])
    item = report.items[0]
    assert "lengthen" in " ".join(item.missing).lower()


@pytest.mark.asyncio
async def test_long_title_not_serp_safe():
    long_title = "A" * 65
    report = await score_title_clickability([long_title])
    assert report.items[0].serp_safe is False
    assert any("shorten" in m for m in report.items[0].missing)


@pytest.mark.asyncio
async def test_question_format_detected():
    report = await score_title_clickability(["What Is Kubernetes?"])
    item = report.items[0]
    assert "question format" in " ".join(item.signals)


@pytest.mark.asyncio
async def test_empty_titles_raises():
    with pytest.raises(ValueError):
        await score_title_clickability([])


@pytest.mark.asyncio
async def test_turkish_power_words():
    report = await score_title_clickability(
        ["VMware Snapshot: Kolay ve Pratik Rehber"], language="tr"
    )
    item = report.items[0]
    assert any("power word" in s for s in item.signals)
