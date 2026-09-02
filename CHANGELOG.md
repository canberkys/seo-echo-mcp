# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.7.0] — 2026-09-02

### Added

- **`score_title_clickability(titles, keyword, language)` tool** — heuristic CTR scoring for title candidates: power words (7 languages), number presence, question format, SERP-safe length, keyword inclusion, optimal character band. Returns ranked `TitleClickabilityReport` with `signals`, `missing`, and `top_pick`.
- **`analyze_internal_links(content_markdown, site_profile)` tool** — audits internal linking in a draft: counts internal/external links, identifies which existing posts are already linked, surfaces unlinked opportunities via token overlap, flags H2 sections with no links, computes `link_density_score` (0-100), and returns prioritised recommendations.
- **TF-IDF cosine similarity in `check_duplicates`** — replaces Jaccard with IDF-weighted cosine so rare/distinctive terms (product names, technical jargon) are upweighted. A single shared rare term now scores higher than many shared common words. All existing tests pass unchanged.

### Changed

- Tool count: 14 → **17** (`score_title_clickability`, `analyze_internal_links` added; `check_duplicates` algorithm upgraded).
- Server instructions updated to reflect 17 tools and new workflow position of both new tools.
- `tests/test_score_title_clickability.py`: 7 tests (new).
- `tests/test_analyze_internal_links.py`: 7 tests (new).

---

## [0.6.0] — 2026-09-02

### Added

- **Portuguese (PT) language support** — full template module (`pt.py`) with all required exports. AI cliché list (14 phrases), slug transliteration (ã/â/á/à/ç/ê/é/í/õ/ô/ó/ú) and stopwords added for PT.
- **`flesch-pt` readability formula** — Martins et al. (1996) adaptation of Flesch Reading Ease for Portuguese. `formula_used: "flesch-pt"` returned for `language="pt"`.
- **Portuguese passive voice detection** (`_PASSIVE_PT`) — ser/estar auxiliary + -ado/-ido past participle pattern. WPM calibrated to 200 for reading-time calculation.
- **French readability formula** — Kandel & Moles (1958): `209 − 1.15×avg_sw − 68.0×avg_syl`. `formula_used: "kandel-moles-fr"` returned for `language="fr"`, replacing the generic heuristic.
- **AI cliché saturation score** in `audit_content` — message now reports `N/total phrases (X% saturation)` so writers can see how generic their draft is at a glance. Severity escalates from `warning` to `error` when ≥30% of the watchlist is present.
- **Smithery + Glama manifests updated** for v0.5.0+: install command switched to `uvx seo-echo-mcp` (PyPI), Italian and multilingual tags added.

### Changed

- Supported language set: EN, TR, DE, FR, ES, IT → **EN, TR, DE, FR, ES, IT, PT**
- `tests/test_readability.py`: 15 → **18 tests** (FR Kandel-Moles, PT Flesch, PT passive).
- `tests/test_audit_content.py`: 6 → **7 tests** (AI cliché density assertion).

---

## [0.5.0] — 2026-09-02

### Added

- **Italian (IT) language support** — full template module (`it.py`) with all required exports: title/meta/H2/FAQ/TITLE_VARIANT templates, synthetic H2 variants, must-cover checklists, image alt templates, CTA, and meta angles. AI cliché list, slug transliteration (à/è/ì/ò/ù) and stopwords added for IT.
- **Gulpease Index formula** — Italian readability scored with the Lucisano & Piemontese 1988 Gulpease Index (`formula_used: "gulpease-it"`), replacing the generic formula for `language="it"`.
- **Italian passive voice detection** (`_PASSIVE_IT`) — essere/venire auxiliary + past participle pattern (-ato/-ita/-uto endings).
- **French passive voice detection** (`_PASSIVE_FR`) — être-family auxiliary + agreeing past participle. `readability_report` now returns a non-null `passive_voice_ratio` for `language="fr"`.
- **Spanish passive voice detection** (`_PASSIVE_ES`) — ser/estar-family auxiliary + -ado/-ido past participle. `readability_report` now returns a non-null `passive_voice_ratio` for `language="es"`.
- **`reading_time_seconds` field** on `ReadabilityReport` — `ceil(word_count / WPM * 60)` using language-specific WPM reference values (EN 238, FR 195, ES 220, IT 200, DE 179, TR 180; fallback 200). Available for all 14 tools that call `readability_report`.
- **PyPI OIDC trusted publishing** — `publish.yml` now triggers automatically on GitHub Release publication in addition to manual `workflow_dispatch`. Requires the `release` environment and a Trusted Publisher entry on PyPI (see README).

### Changed

- Supported language set: EN, TR, DE, FR, ES → **EN, TR, DE, FR, ES, IT**
- `tests/test_readability.py`: 8 → **15 tests** covering IT Gulpease, IT/FR/ES passive detection, reading-time computation for EN and TR.

---

## [0.4.0] — 2026-04-23

### Security

- **Cache path hardening** — `analyze_site` now sanitizes the domain used as a cache filename via `Path(domain).name` + character filter, blocking path-traversal-shaped inputs (`../evil`, `/etc/passwd`) from escaping `~/.cache/seo-echo-mcp/`.
- **HTTP response size limits** — `analyze_site`, `analyze_competitors`, and underlying extractors reject responses larger than 5 MB to avoid memory-exhaustion scenarios on pathological pages.

### Fixed — language-aware output (previously English-only fallbacks leaked through)

- **`generate_outline` synthetic H2s are now per-language** — long Turkish/French/German/Spanish outlines no longer emit `"Advanced X techniques"` or `"X in practice"` in English when the template pool runs out. Added `SYNTHETIC_H2_VARIANTS`, `MUST_COVER_{INTRO,CORE,TOPIC,SUMMARY}`, `H2_STYLE_TEMPLATES`, `SUMMARY_H2`, `TOPIC_CONNECTOR` to every language module.
- **`_apply_h2_style`, `_format_h2`, `_summary_h2`** read from the language template instead of hardcoded English strings.
- **Tone jargon detection is per-language** (`TONE_JARGON_BY_LANG`) so a single English loanword in a Turkish blog no longer flips the tone to `technical`. Threshold raised 1% → 1.5%.
- **TR passive regex** validated against active-voice past-tense text to keep false-positive ratio below 1.0; DE passive tested against active-voice sentences (ratio == 0.0).

### Added — quality

- **Turkish morphology-aware tokenization** (`utils.text.stem_tr`) — suffix stripper handles `-lar/-ler/-ı/-i/-dır/-'ı/-'ları` etc. so `check_duplicates` collapses inflections (`snapshot'ları` ≡ `snapshot`).
- **`suggest_image_alts` is language-aware** — alt-text templates come from `IMAGE_ALT_TEMPLATES` in each language module. Weak-alt blacklist expanded with TR/ES/DE equivalents (`resim`, `görsel`, `imagen`, `bild`, …).
- **Pronoun families in `_addressing`** — `PRONOUN_FAMILIES` collapses `sen/senin/sana/seni` to a single "sen" score (vs four separate candidates previously). `siz` family tracked independently for proper TR distinction. Same pattern for FR `tu` vs `vous`, DE `du` vs `Sie`, ES `tú` / `usted` / `vosotros`.
- **Stratified sample selection** (`analyze_site._select_samples`) — previous `head + tail` strategy skipped the middle 50%. Stride-sampling now covers the sitemap evenly.
- **Logging + empty-input validation** across all 14 tools — `logger.info(...)` milestones + early `ValueError` on blank strings.
- **`TypedDict` returns for extractors** — `ExtractedPost` / `ExtractedStructure` replace `dict[str, Any]`.

### Added — DX / ecosystem

- **`SECURITY.md`**, **`CODE_OF_CONDUCT.md`** (Contributor Covenant 2.1), **`.github/dependabot.yml`** (weekly pip + gh-actions).
- **`examples/`** folder with realistic anonymized artifacts (`site_profile.json`, `outline.json`, `audit_report.json`, `draft_skeleton.md`, `content_gap_report.json`).
- **README "Use as a Python library"**, **"Troubleshooting"**, and **"What this MCP does NOT do"** sections.
- **Full 14-tool API Reference** (previously only 4 tools were documented).
- **Codecov** upload from CI (Python 3.13 matrix) + badge + `codecov.yml` (70% project target).
- **Registry manifests**: `smithery.yaml` (Smithery.ai auto-discovery) and `glama.json` (Glama.ai) at the repo root. `docs/REGISTRY_SUBMISSIONS.md` tracks state + copy-paste templates for awesome-mcp-servers / mcp-get PRs.

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
