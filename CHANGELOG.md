# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.3.0] — 2026-04-21

### Added

- **`suggest_image_alts`** — new tool (14 total). Parses markdown images, flags missing/weak alt text, and proposes replacements derived from the filename stem, the target keyword, and the nearest preceding paragraph. No LLM call.
- **`analyze_site` now accepts `urls: list[str]`** — explicit post URLs skip sitemap/feed discovery entirely. Useful for JS-rendered sites, paywalled blogs, or blogs whose sitemap is blocked/missing.
- **Persistent cache for `analyze_site`** — profiles are stored at `~/.cache/seo-echo-mcp/<domain>.json` (override via `SEO_ECHO_CACHE_DIR` env var). TTL defaults to 24h; `cache_ttl=0` disables caching, `bypass_cache=True` forces a re-crawl.
- **Turkish and German passive-voice detection** in `readability_report`. The `passive_voice_ratio` field is now populated for English, Turkish, and German drafts (other languages still return `None` until a regex lands).
- **`CONTRIBUTING.md`**, issue templates (bug + feature), and PR template. "Adding a language" and "Adding a tool" are documented step-by-step.

### Changed

- `analyze_site` signature: `url` and `urls` are now both optional — pass one or the other. Backward compatible with all `analyze_site("domain.tld")` callsites.

## [0.2.1] — 2026-04-21

### Fixed

- `generate_outline`: section H2s are now guaranteed to be unique. Previously the template pool could recycle the same heading across sections when the outline was long or competitor topics ran out (observed as two "Key principles of X" sections). A 12-variant synthetic pool plus a used-H2 set backs the fix, and a last-resort numeric suffix prevents any collision.
- `generate_outline` + `suggest_titles`: keyword casing is preserved. Earlier both tools ran `keyword.title()` when the input was lowercase, which broke proper nouns ("VMware vMotion" → "Vmware Vmotion"). Input is now kept verbatim.

### Added

- `suggest_titles` now reads the most common N from competitor titles (range 3–50) and uses it when filling listicle templates. Suggestions mirror the shape SERP competitors are already using ("Top 10 …" instead of a hard-coded 7).
- Stderr logging in `server.py`: structured lines written to stderr (stdout stays reserved for the MCP protocol). Configure verbosity via the `SEO_ECHO_LOG_LEVEL` env var (default `INFO`). `analyze_site` and `analyze_competitors` emit start/finish milestones so multi-tool chains are debuggable in IDE logs.

### Changed

- CI: `ruff check` and `ruff format --check` both pass; all-matrix (Py 3.10–3.13) green.
- `publish.yml` is `workflow_dispatch`-only; the `environment: release` key was removed so GitHub Releases no longer leave fail-state deployment records. Re-enable both when PyPI trusted publishing is configured.
- Installation: default path is `uvx --from git+https://github.com/canberkys/seo-echo-mcp seo-echo-mcp`. PyPI path kept as an optional future fallback.
- README: IDE Setup is now a set of collapsible `<details>` blocks per IDE; badges updated (CI + release, PyPI badge removed until published).
- Repo discoverability: GitHub About + 20 topics set, `pyproject.toml` keywords expanded (29 terms, mirrors topic list).

### Removed

- `docs/build-spec.md` — original development artifact with placeholder fields; not useful in a public repo.

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
