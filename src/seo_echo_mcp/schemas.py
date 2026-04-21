"""Pydantic models shared across tools.

Input/output contracts for every public tool in this MCP server. Keeping them
here lets tool modules depend on schemas without circular imports.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PostSample(BaseModel):
    """One existing post sampled from the target blog."""

    url: str
    title: str
    h2s: list[str]
    word_count: int
    category: str | None = None
    snippet: str
    published_at: str | None = None


class StyleProfile(BaseModel):
    """Heuristic-derived voice/style profile of a blog."""

    average_word_count: int
    tone: Literal["formal", "informal", "technical", "conversational", "journalistic", "mixed"]
    addressing: str
    h2_pattern: Literal["question", "statement", "imperative", "mixed"]
    uses_lists: bool
    uses_code_blocks: bool
    avg_paragraph_sentences: float
    em_dash_frequency: Literal["frequent", "occasional", "rare", "never"]
    avg_sentence_words: float


class SiteProfile(BaseModel):
    """Full profile of a blog: language, topics, style, sampled posts."""

    domain: str
    url: str
    language: str
    language_confidence: Literal["high", "medium", "mixed"]
    sampled_at: str
    sample_count: int
    sample_urls: list[str]
    categories: list[str]
    topics: list[str]
    style: StyleProfile
    existing_posts: list[PostSample]


class SerpEntry(BaseModel):
    """One competitor result fetched from SERP or provided directly."""

    url: str
    title: str
    position: int
    snippet: str
    h2s: list[str]
    word_count: int
    has_schema: bool
    schema_types: list[str]
    internal_link_count: int
    external_link_count: int


class CompetitorInsights(BaseModel):
    """Aggregate insights across competitor pages."""

    average_word_count: int
    word_count_range: tuple[int, int]
    common_h2_topics: list[str]
    dominant_format: Literal[
        "listicle", "guide", "comparison", "tutorial", "review", "news", "mixed"
    ]
    title_patterns: list[str]
    schema_adoption_pct: float
    avg_internal_links: int
    avg_external_links: int


class CompetitorAnalysis(BaseModel):
    """Top-SERP competitor analysis result."""

    keyword: str | None
    language: str
    country: str
    fetched_at: str
    results: list[SerpEntry]
    insights: CompetitorInsights


class OutlineSection(BaseModel):
    """One section of a generated outline."""

    h2: str
    purpose: str
    word_count_target: int
    must_cover: list[str]
    suggested_visuals: list[str]


class Outline(BaseModel):
    """SEO-optimized outline tailored to a site's voice."""

    keyword: str
    language: str
    suggested_titles: list[str]
    suggested_meta_descriptions: list[str]
    word_count_target: int
    h2_style: str
    addressing: str
    category: str
    sections: list[OutlineSection]
    recommended_internal_link_targets: list[str]
    external_citation_topics: list[str]
    cta_suggestion: str


class Check(BaseModel):
    """One audit check result.

    Uses `pass_` because `pass` is a reserved keyword; serialized as `"pass"`
    in JSON via Pydantic alias.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    pass_: bool = Field(alias="pass")
    severity: Literal["error", "warning", "info"]
    actual: str | int | float | list | None = None
    expected: str | int | float | None = None
    message: str


class AuditReport(BaseModel):
    """Full audit report for a content draft."""

    overall_score: int
    passed_count: int
    warning_count: int
    error_count: int
    checks: list[Check]
    recommendations: list[str]
    reading_time_minutes: int
    word_count: int
    detected_language: str


# ---------- v0.2 content-creation models ----------


class TitleSuggestion(BaseModel):
    """One suggested title with SERP-safety metadata."""

    title: str
    length: int
    pattern: Literal[
        "listicle", "question", "how-to", "comparison", "year", "benefit", "curiosity", "statement"
    ]
    serp_safe: bool  # True if length <= 60 chars
    matches_site_style: bool


class TitleSuggestions(BaseModel):
    """Ranked list of title candidates for a keyword."""

    keyword: str
    language: str
    items: list[TitleSuggestion]
    primary_recommendation: str


class MetaVariation(BaseModel):
    """One meta description variation."""

    description: str
    angle: Literal["problem-solution", "question", "benefit", "curiosity", "action"]
    length: int
    keyword_present: bool


class MetaVariations(BaseModel):
    """Set of meta description variations for A/B testing."""

    keyword: str
    title: str
    language: str
    items: list[MetaVariation]


class SlugResult(BaseModel):
    """URL-safe slug + short alternatives."""

    primary: str
    alternatives: list[str]
    language: str
    original_title: str


class FaqItem(BaseModel):
    """One FAQ question paired with a write directive for the host LLM."""

    position: int
    question: str
    answer_directive: str  # HTML comment like <!-- WRITE: 60-80 words, cite source -->


class FaqSection(BaseModel):
    """FAQ section ready to embed in a post draft."""

    keyword: str
    language: str
    items: list[FaqItem]
    markdown: str
    faq_jsonld: str


class SchemaJsonLd(BaseModel):
    """JSON-LD structured data block."""

    schema_type: Literal["Article", "BlogPosting", "HowTo", "Review"]
    json_ld: str
    html_snippet: str


class ContentGap(BaseModel):
    """One uncovered topic the site could address."""

    topic: str
    coverage_count: int  # how many competitors cover it
    competing_urls: list[str]
    suggested_angle: str


class ContentGapReport(BaseModel):
    """Topics where the site lags behind top competitors."""

    site_url: str
    keyword_scope: str | None
    gaps: list[ContentGap]
    summary: str


class DuplicateMatch(BaseModel):
    """One existing post that overlaps with the proposed keyword/title."""

    existing_url: str
    existing_title: str
    overlap_score: float  # Jaccard, 0.0-1.0
    reason: str


class DuplicateReport(BaseModel):
    """Duplication risk for a proposed keyword/title."""

    proposed: str
    matches: list[DuplicateMatch]
    verdict: Literal["safe", "caution", "duplicate"]


class ReadabilityReport(BaseModel):
    """Per-language readability metrics."""

    language: str
    formula_used: str  # "flesch-en", "atesman-tr", "fernandez-huerta-es", "generic"
    score: float
    verdict: Literal["easy", "medium", "hard"]
    grade_level: float
    word_count: int
    sentence_count: int
    avg_sentence_words: float
    avg_syllables_per_word: float
    passive_voice_ratio: float | None  # None when not computed (non-English)


class DraftSkeleton(BaseModel):
    """Full markdown skeleton handed to the host LLM for drafting."""

    keyword: str
    language: str
    slug: str
    frontmatter: dict
    markdown: str
    word_count_target: int
    section_count: int
    has_faq: bool
    has_schema: bool


class ImageAltSuggestion(BaseModel):
    """One image in the draft with an alt-text analysis."""

    position: int
    src: str
    current_alt: str
    status: Literal["missing", "weak", "ok"]
    suggested_alts: list[str]
    context_snippet: str


class ImageAltReport(BaseModel):
    """Alt-text audit for every image in a markdown draft."""

    image_count: int
    missing_count: int
    weak_count: int
    items: list[ImageAltSuggestion]


def apply_voice_overrides(site_profile: SiteProfile, overrides: dict | None) -> SiteProfile:
    """Return a copy of `site_profile` with `StyleProfile` fields overridden.

    Used by tools that accept a `voice_overrides` argument. The original object
    is never mutated — the call goes through Pydantic's `model_copy(update=...)`
    so type validation still applies (invalid keys or values raise
    `ValidationError`).

    Typical use: a user whose existing blog uses em-dashes occasionally but
    wants new drafts to avoid them passes
    `voice_overrides={"em_dash_frequency": "never"}`.
    """
    if not overrides:
        return site_profile
    new_style = site_profile.style.model_copy(update=overrides)
    return site_profile.model_copy(update={"style": new_style})
