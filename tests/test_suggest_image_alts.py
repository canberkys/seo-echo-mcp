"""Smoke tests for suggest_image_alts."""

from __future__ import annotations

import pytest

from seo_echo_mcp.tools.suggest_image_alts import suggest_image_alts


@pytest.mark.asyncio
async def test_flags_missing_alt():
    draft = "# Post\n\nSome intro text.\n\n![](https://ex.test/img/screenshot.png)\n"
    report = await suggest_image_alts(draft)
    assert report.image_count == 1
    assert report.missing_count == 1
    assert report.items[0].status == "missing"
    # The filename stem should appear somewhere in the suggestions.
    assert any("screenshot" in s.lower() for s in report.items[0].suggested_alts)


@pytest.mark.asyncio
async def test_flags_weak_generic_alt():
    draft = "# Post\n\n![image](https://ex.test/x.png)\n"
    report = await suggest_image_alts(draft, target_keyword="kubernetes ingress")
    assert report.items[0].status == "weak"
    assert any("kubernetes ingress" in s.lower() for s in report.items[0].suggested_alts)


@pytest.mark.asyncio
async def test_ok_alt_not_flagged():
    draft = (
        "# Post\n\n"
        "This diagram shows how vMotion transfers state across hosts.\n\n"
        "![Diagram of vMotion state transfer between two ESXi hosts]"
        "(https://ex.test/vmotion-flow.png)\n"
    )
    report = await suggest_image_alts(draft, target_keyword="vmware vmotion")
    assert report.items[0].status == "ok"
    assert report.missing_count == 0
    assert report.weak_count == 0


@pytest.mark.asyncio
async def test_multiple_images_positions_are_sequential():
    draft = "# Post\n\n![](https://ex.test/a.png)\n\nSome text.\n\n![logo](https://ex.test/b.png)\n"
    report = await suggest_image_alts(draft)
    assert [i.position for i in report.items] == [1, 2]
    assert report.items[0].status == "missing"
    assert report.items[1].status == "weak"
