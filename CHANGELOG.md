# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.2.0] — 2026-04-21

### Added — content creator expansion

Nine new tools turn the MCP into a full end-to-end content workflow (no extra LLM/API calls — all rule/template-based).

- `prepare_draft_skeleton` — assembles a markdown skeleton (YAML frontmatter, voice-aware `<!-- WRITE -->` directives per section, internal link/citation slots, optional FAQ + JSON-LD) for the host LLM to fill.
- `suggest_titles` — 10 SEO title candidates, voice-matched to the site's H2 pattern.
- `generate_meta_variations` — 5 meta descriptions across 5 angles (problem/question/benefit/curiosity/action), 140–160 chars.
- `generate_slug` — URL-safe slug with language-aware transliteration (Turkish `ı→i`, German `ü→ue`, etc.) plus short alternatives.
- `generate_faq_section` — PAA-style FAQ block (markdown) + FAQPage JSON-LD; pulls question-shaped H2s from competitor analysis if provided.
- `generate_schema_jsonld` — Article / BlogPosting / HowTo / Review JSON-LD plus ready-to-paste `<script>` snippet.
- `detect_content_gaps` — topics competitors cover but the site doesn't, ranked by coverage count.
- `check_duplicates` — Jaccard-based overlap warning against existing posts.
- `readability_report` — per-language formulas (Flesch-EN, Ateşman-TR, Fernández-Huerta-ES, generic fallback) + passive voice ratio for English.
- `voice_overrides: dict | None` parameter on `prepare_draft_skeleton` and `audit_content`. Lets callers override `StyleProfile` fields (e.g. `{"em_dash_frequency": "never"}`) for editorial preferences that differ from what `analyze_site` measured on the existing blog. Backed by an `apply_voice_overrides()` helper in `schemas.py`.

### Changed

- Extracted `_strip_frontmatter`, `_markdown_to_plain`, `_headings` from `audit_content.py` into shared `utils/text.py`.
- Extended `config/templates/{en,tr,es,fr,de}.py` with `META_ANGLES`, `FAQ_QUESTION_TEMPLATES`, `TITLE_VARIANT_TEMPLATES`.
- Added `config/slug_rules.py` for per-language character maps and stopwords.
- `server.py` instructions field documents the full chain so host LLMs can plan multi-tool invocations.

## [0.1.0] — 2026-04-21

### Added
- Initial release.
- `analyze_site` tool: blog crawling + style/topic profile extraction.
- `analyze_competitors` tool: SERP analysis via DuckDuckGo with Bing HTML fallback, optional Google Custom Search.
- `generate_outline` tool: rule-based, voice-preserving outline generation.
- `audit_content` tool: rule-based content scoring against site profile and SEO best practices.
- Built-in AI cliché detection for Turkish, English, Spanish, French, German.
