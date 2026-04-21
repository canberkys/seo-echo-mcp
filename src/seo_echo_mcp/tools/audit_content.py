"""audit_content: rule-based scoring of a markdown draft against a site profile."""

from __future__ import annotations

import re

import py3langid

from seo_echo_mcp.config.ai_cliches import cliches_for
from seo_echo_mcp.config.seo_rules import (
    KEYWORD_DENSITY_MAX,
    KEYWORD_DENSITY_MIN,
    META_DESC_MAX,
    META_DESC_MIN,
    MIN_EXTERNAL_LINKS,
    MIN_INTERNAL_LINKS,
    READING_WPM,
    SEVERITY_WEIGHTS,
    WORD_COUNT_TOLERANCE,
)
from seo_echo_mcp.schemas import AuditReport, Check, SiteProfile, apply_voice_overrides
from seo_echo_mcp.utils.text import markdown_to_plain, split_headings, strip_frontmatter


async def audit_content(
    content_markdown: str,
    site_profile: SiteProfile,
    target_keyword: str | None = None,
    target_meta_description: str | None = None,
    voice_overrides: dict | None = None,
) -> AuditReport:
    """Score a markdown draft against site voice and SEO best practices.

    Args:
        content_markdown: Full markdown body; optional YAML frontmatter tolerated.
        site_profile: Profile produced by `analyze_site` for this site.
        target_keyword: If provided, keyword-presence/density checks run.
        target_meta_description: If provided, length check runs.
        voice_overrides: Optional dict to override StyleProfile fields for this
            audit (e.g. `{"em_dash_frequency": "never"}` to enforce a stricter
            editorial policy than the site's own history shows).

    Returns:
        AuditReport with pass/fail per check, overall score, and recommendations.
    """
    site_profile = apply_voice_overrides(site_profile, voice_overrides)
    body = strip_frontmatter(content_markdown)
    plain = markdown_to_plain(body)
    words = re.findall(r"[\w’']+", plain)
    word_count = len(words)
    h1, h2s, h3s = split_headings(body)
    detected_lang, _ = py3langid.classify(plain) if plain else ("en", 0.0)

    checks: list[Check] = []
    checks.append(_check_word_count(word_count, site_profile))
    checks.append(_check_h2_format(h2s, site_profile))
    checks.append(_check_em_dash(body, site_profile))
    checks.extend(_check_ai_cliches(plain, site_profile.language))
    checks.append(_check_addressing(plain, site_profile))
    checks.append(_check_heading_hierarchy(h1, h2s, h3s))
    checks.append(_check_paragraph_length(body, site_profile))
    checks.append(_check_sentence_length(plain, site_profile))
    checks.append(_check_image_alt(body))

    internal_links, external_links = _count_links(body, site_profile.domain)
    checks.append(_check_link_count("internal_links_count", internal_links, MIN_INTERNAL_LINKS))
    checks.append(_check_link_count("external_citations_count", external_links, MIN_EXTERNAL_LINKS))

    if target_keyword:
        checks.append(_check_keyword_in_title(h1, target_keyword))
        checks.append(_check_keyword_density(plain, target_keyword, word_count))
        checks.append(_check_keyword_in_first_paragraph(body, target_keyword))
    if target_meta_description is not None:
        checks.append(_check_meta_description_length(target_meta_description))

    passed = sum(1 for c in checks if c.pass_)
    warnings = sum(1 for c in checks if not c.pass_ and c.severity == "warning")
    errors = sum(1 for c in checks if not c.pass_ and c.severity == "error")
    score = _score(checks)

    recommendations = [
        c.message
        for c in sorted(checks, key=lambda x: -SEVERITY_WEIGHTS.get(x.severity, 0))
        if not c.pass_
    ][:8]

    reading_minutes = max(1, round(word_count / READING_WPM))

    return AuditReport(
        overall_score=score,
        passed_count=passed,
        warning_count=warnings,
        error_count=errors,
        checks=checks,
        recommendations=recommendations,
        reading_time_minutes=reading_minutes,
        word_count=word_count,
        detected_language=detected_lang,
    )


def _check_word_count(wc: int, sp: SiteProfile) -> Check:
    target = sp.style.average_word_count or 1200
    lo = int(target * (1 - WORD_COUNT_TOLERANCE))
    hi = int(target * (1 + WORD_COUNT_TOLERANCE))
    ok = lo <= wc <= hi
    return Check(
        name="word_count",
        pass_=ok,
        severity="warning",
        actual=wc,
        expected=f"{lo}-{hi}",
        message=f"Word count {wc} outside preferred {lo}-{hi}."
        if not ok
        else "Word count in range.",
    )


def _check_h2_format(h2s: list[str], sp: SiteProfile) -> Check:
    if not h2s:
        return Check(
            name="h2_format",
            pass_=False,
            severity="warning",
            actual=0,
            expected=">=1 H2",
            message="No H2 headings found.",
        )
    pattern = sp.style.h2_pattern
    match_ratio = _h2_match_ratio(h2s, pattern)
    ok = match_ratio >= 0.7 or pattern == "mixed"
    return Check(
        name="h2_format",
        pass_=ok,
        severity="error" if not ok else "info",
        actual=round(match_ratio, 2),
        expected=f">=0.70 for pattern '{pattern}'",
        message=(
            f"Only {int(match_ratio * 100)}% of H2s match site pattern '{pattern}'."
            if not ok
            else f"H2s align with site pattern '{pattern}'."
        ),
    )


def _h2_match_ratio(h2s: list[str], pattern: str) -> float:
    if not h2s:
        return 0.0
    if pattern == "question":
        return sum(1 for h in h2s if h.rstrip().endswith("?")) / len(h2s)
    if pattern == "statement":
        return sum(1 for h in h2s if not h.rstrip().endswith("?")) / len(h2s)
    if pattern == "imperative":
        # very rough: starts with verb-like token (no punctuation mid-word)
        return sum(1 for h in h2s if h.strip() and h.strip()[0].isalpha()) / len(h2s)
    return 1.0  # mixed accepts anything


def _check_em_dash(body: str, sp: SiteProfile) -> Check:
    count = body.count("—")
    freq = sp.style.em_dash_frequency
    if freq == "never" and count > 0:
        return Check(
            name="em_dash_usage",
            pass_=False,
            severity="error",
            actual=count,
            expected=0,
            message=f"Site never uses em-dashes but draft has {count}. Remove them.",
        )
    if freq == "rare" and count > 5:
        return Check(
            name="em_dash_usage",
            pass_=False,
            severity="warning",
            actual=count,
            expected="<=5",
            message=f"Site uses em-dashes rarely; draft has {count}. Reduce usage.",
        )
    return Check(
        name="em_dash_usage",
        pass_=True,
        severity="info",
        actual=count,
        expected=None,
        message="Em-dash usage matches site style.",
    )


def _check_ai_cliches(plain: str, language: str) -> list[Check]:
    lowered = plain.lower()
    hits = [phrase for phrase in cliches_for(language) if phrase in lowered]
    if not hits:
        return [
            Check(
                name="ai_cliches",
                pass_=True,
                severity="info",
                actual=0,
                expected=0,
                message="No AI clichés detected.",
            )
        ]
    return [
        Check(
            name="ai_cliches",
            pass_=False,
            severity="warning",
            actual=hits[:5],
            expected=0,
            message=f"AI-cliché phrases detected ({len(hits)}). Rewrite: {', '.join(hits[:3])}…",
        )
    ]


def _check_addressing(plain: str, sp: SiteProfile) -> Check:
    from seo_echo_mcp.extractors.style import PRONOUNS

    expected = sp.style.addressing
    lowered = plain.lower()
    counts = {
        p: len(re.findall(rf"\b{re.escape(p)}\b", lowered))
        for p in PRONOUNS.get(sp.language, PRONOUNS["en"])
    }
    top = max(counts, key=counts.get) if counts and max(counts.values()) > 0 else "impersonal"
    ok = top == expected or (expected == "impersonal" and sum(counts.values()) < 3)
    return Check(
        name="addressing_consistency",
        pass_=ok,
        severity="warning",
        actual=top,
        expected=expected,
        message=(
            f"Draft addresses reader as '{top}' but site uses '{expected}'."
            if not ok
            else "Addressing matches site."
        ),
    )


def _check_heading_hierarchy(h1: str, h2s: list[str], h3s: list[str]) -> Check:
    ok = bool(h1) and (not h3s or bool(h2s))
    return Check(
        name="headings_hierarchy",
        pass_=ok,
        severity="error" if not ok else "info",
        actual=f"h1={'yes' if h1 else 'no'}, h2={len(h2s)}, h3={len(h3s)}",
        expected="exactly 1 H1, H3s only under H2",
        message="Heading hierarchy is invalid." if not ok else "Heading hierarchy is valid.",
    )


def _check_paragraph_length(body: str, sp: SiteProfile) -> Check:
    paragraphs = [
        p for p in re.split(r"\n\s*\n", body) if p.strip() and not p.lstrip().startswith("#")
    ]
    if not paragraphs:
        return Check(
            name="paragraph_length",
            pass_=False,
            severity="warning",
            actual=0,
            expected=sp.style.avg_paragraph_sentences,
            message="No body paragraphs detected.",
        )
    lengths = []
    for p in paragraphs:
        sents = [s for s in re.split(r"[.!?]+", p) if s.strip()]
        if sents:
            lengths.append(len(sents))
    avg = sum(lengths) / max(len(lengths), 1)
    target = sp.style.avg_paragraph_sentences or 3.0
    ok = abs(avg - target) <= 2
    return Check(
        name="paragraph_length",
        pass_=ok,
        severity="warning",
        actual=round(avg, 2),
        expected=target,
        message=(
            f"Avg paragraph length {avg:.1f} deviates from site avg {target:.1f}."
            if not ok
            else "Paragraph length matches site."
        ),
    )


def _check_sentence_length(plain: str, sp: SiteProfile) -> Check:
    sents = [s for s in re.split(r"[.!?]+", plain) if s.strip()]
    if not sents:
        return Check(
            name="sentence_length",
            pass_=False,
            severity="warning",
            actual=0,
            expected=sp.style.avg_sentence_words,
            message="No sentences detected.",
        )
    avg = sum(len(re.findall(r"\S+", s)) for s in sents) / len(sents)
    target = sp.style.avg_sentence_words or 18.0
    ok = abs(avg - target) <= 5
    return Check(
        name="sentence_length",
        pass_=ok,
        severity="warning",
        actual=round(avg, 2),
        expected=target,
        message=(
            f"Avg sentence length {avg:.1f} deviates from site avg {target:.1f}."
            if not ok
            else "Sentence length matches site."
        ),
    )


def _check_image_alt(body: str) -> Check:
    empties = re.findall(r"!\[\s*\]\([^)]+\)", body)
    ok = not empties
    return Check(
        name="image_alt_coverage",
        pass_=ok,
        severity="error" if not ok else "info",
        actual=len(empties),
        expected=0,
        message=(
            f"{len(empties)} image(s) missing alt text." if not ok else "All images have alt text."
        ),
    )


def _count_links(body: str, domain: str) -> tuple[int, int]:
    links = re.findall(r"\[[^\]]+\]\((https?://[^)]+)\)", body)
    internal = sum(1 for href in links if domain in href)
    external = len(links) - internal
    # Also count bare https URLs not inside markdown link brackets
    bare = re.findall(r"(?<!\()\bhttps?://[^\s)]+", body)
    for href in bare:
        if href in links:
            continue
        if domain in href:
            internal += 1
        else:
            external += 1
    return internal, external


def _check_link_count(name: str, actual: int, minimum: int) -> Check:
    ok = actual >= minimum
    return Check(
        name=name,
        pass_=ok,
        severity="warning",
        actual=actual,
        expected=f">={minimum}",
        message=(
            f"{name.replace('_', ' ')} {actual} below target {minimum}."
            if not ok
            else f"{name.replace('_', ' ')} meets target."
        ),
    )


def _check_keyword_in_title(h1: str, keyword: str) -> Check:
    ok = keyword.lower() in h1.lower() if h1 else False
    return Check(
        name="keyword_in_title",
        pass_=ok,
        severity="error" if not ok else "info",
        actual=h1 or None,
        expected=keyword,
        message=(
            f"Target keyword '{keyword}' missing from title."
            if not ok
            else "Keyword present in title."
        ),
    )


def _check_keyword_density(plain: str, keyword: str, word_count: int) -> Check:
    if word_count == 0:
        density = 0.0
    else:
        occurrences = len(re.findall(rf"\b{re.escape(keyword)}\b", plain, flags=re.IGNORECASE))
        density = occurrences / word_count
    ok = KEYWORD_DENSITY_MIN <= density <= KEYWORD_DENSITY_MAX
    return Check(
        name="keyword_density",
        pass_=ok,
        severity="warning",
        actual=round(density * 100, 2),
        expected=f"{KEYWORD_DENSITY_MIN * 100:.1f}-{KEYWORD_DENSITY_MAX * 100:.1f}%",
        message=(
            f"Keyword density {density * 100:.2f}% outside target band."
            if not ok
            else "Keyword density in target range."
        ),
    )


def _check_keyword_in_first_paragraph(body: str, keyword: str) -> Check:
    paragraphs = [
        p for p in re.split(r"\n\s*\n", body) if p.strip() and not p.lstrip().startswith("#")
    ]
    first = paragraphs[0] if paragraphs else ""
    ok = keyword.lower() in first.lower()
    return Check(
        name="keyword_in_first_paragraph",
        pass_=ok,
        severity="warning",
        actual=None,
        expected=keyword,
        message=(
            "Target keyword missing from first paragraph."
            if not ok
            else "Keyword present in opening paragraph."
        ),
    )


def _check_meta_description_length(meta: str) -> Check:
    n = len(meta)
    ok = META_DESC_MIN <= n <= META_DESC_MAX
    return Check(
        name="meta_description_length",
        pass_=ok,
        severity="warning",
        actual=n,
        expected=f"{META_DESC_MIN}-{META_DESC_MAX}",
        message=(
            f"Meta description {n} chars; target {META_DESC_MIN}-{META_DESC_MAX}."
            if not ok
            else "Meta description length in target."
        ),
    )


def _score(checks: list[Check]) -> int:
    deduction = sum(SEVERITY_WEIGHTS.get(c.severity, 0) for c in checks if not c.pass_)
    return max(0, 100 - deduction)
