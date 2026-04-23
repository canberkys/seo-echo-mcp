# seo-echo-mcp

**Voice-preserving SEO content MCP server — 14 rule-based tools, language-agnostic, no external LLM calls.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![Test](https://github.com/canberkys/seo-echo-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/canberkys/seo-echo-mcp/actions/workflows/test.yml)
[![GitHub release](https://img.shields.io/github/v/release/canberkys/seo-echo-mcp)](https://github.com/canberkys/seo-echo-mcp/releases)
[![codecov](https://codecov.io/gh/canberkys/seo-echo-mcp/graph/badge.svg)](https://codecov.io/gh/canberkys/seo-echo-mcp)

[Features](#features) • [Installation](#installation) • [IDE Setup](#ide-setup) • [API Reference](#api-reference) • [Contributing](#contributing)

---

## What is this?

Most SEO MCPs give you keyword data. **seo-echo-mcp is different:** it reads your existing blog, extracts your writing voice, and makes sure new SEO content matches that voice — in any language.

Think of it as giving your LLM assistant a "style mirror" for your content.

## Features

14 tools covering the full pipeline from site analysis through publish-ready draft + schema + image-alt audit. Every tool is rule/template-based — **no external LLM/API calls**.

### Research & strategy

| Tool | What it does |
|---|---|
| `analyze_site` | Crawls your blog, extracts language, topics, style profile, H2 patterns |
| `analyze_competitors` | Fetches top SERP results (DuckDuckGo → Bing fallback) and extracts their structure |
| `detect_content_gaps` | Surfaces topics competitors cover but you don't |
| `check_duplicates` | Warns when a proposed keyword/title overlaps with existing posts |

### Structure & metadata

| Tool | What it does |
|---|---|
| `suggest_titles` | 10 SEO title candidates, ranked by site voice + competitor format |
| `generate_meta_variations` | 5 meta descriptions across 5 angles (140-160 chars) |
| `generate_slug` | URL-safe slug with language-aware transliteration (ı→i, ü→ue, ñ→n…) |
| `generate_outline` | SEO outline matched to your voice + competitor common H2 topics |
| `generate_faq_section` | PAA-style FAQ block + FAQPage JSON-LD |
| `generate_schema_jsonld` | Article / BlogPosting / HowTo / Review JSON-LD |

### Draft scaffolding & post-draft quality

| Tool | What it does |
|---|---|
| `prepare_draft_skeleton` | Full markdown skeleton with frontmatter + `<!-- WRITE -->` directives per section. Host LLM fills and saves the `.md`. |
| `audit_content` | Scores a draft against your style profile + 16 SEO checks |
| `readability_report` | Per-language readability (Flesch-EN, Ateşman-TR, Fernández-Huerta-ES, generic fallback) + passive voice (EN/TR/DE) |
| `suggest_image_alts` | Flags missing/weak `<img>` alt text and proposes replacements from filename + context |

### Overriding voice heuristics

`analyze_site` measures the voice of your **existing** posts. If your editorial preference differs — e.g. "my blog uses em-dashes occasionally but I don't want them in new drafts" — pass `voice_overrides` to `prepare_draft_skeleton` and `audit_content`:

```python
voice_overrides = {"em_dash_frequency": "never"}
```

Any `StyleProfile` field can be overridden this way (`em_dash_frequency`, `addressing`, `tone`, `average_word_count`, …). The site profile itself is not mutated — the override only affects that single tool call.

## Language support

Works with **any language** that has an ISO 639-1 code. Built-in AI cliché detection for: Turkish, English, Spanish, French, German (contributions welcome for more).

## Installation

No manual install required — run it straight from GitHub with `uvx`:

```bash
uvx --from git+https://github.com/canberkys/seo-echo-mcp seo-echo-mcp
```

`uvx` clones + builds on first run, caches afterwards. To pin a specific version append `@v0.4.0` to the git URL. To refresh after a new commit: `uvx --refresh ...`.

<details>
<summary>Other installation methods</summary>

**Persistent pip install (no PyPI):**

```bash
pip install git+https://github.com/canberkys/seo-echo-mcp
# or with uv:
uv pip install git+https://github.com/canberkys/seo-echo-mcp
```

**Local clone for development:**

```bash
git clone https://github.com/canberkys/seo-echo-mcp && cd seo-echo-mcp
uv sync --extra dev
uv run seo-echo-mcp   # stdio server for testing
```

**From PyPI:** not published yet. Track [issue #TBD](https://github.com/canberkys/seo-echo-mcp/issues) for PyPI release.

</details>

## IDE Setup

Click the IDE you use to expand setup instructions.

<details>
<summary><b>Claude Code</b></summary>

```bash
claude mcp add seo-echo --scope user -- uvx --from git+https://github.com/canberkys/seo-echo-mcp seo-echo-mcp
```

Then in any Claude Code session, type `/mcp` — you should see `seo-echo ✓ Connected`.

</details>

<details>
<summary><b>Claude Desktop</b></summary>

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "seo-echo": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/canberkys/seo-echo-mcp",
        "seo-echo-mcp"
      ]
    }
  }
}
```

Restart Claude Desktop. The tools appear under the 🔌 icon.

</details>

<details>
<summary><b>Cursor</b></summary>

Create `.cursor/mcp.json` in your project root (or `~/.cursor/mcp.json` for a global install):

```json
{
  "mcpServers": {
    "seo-echo": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/canberkys/seo-echo-mcp",
        "seo-echo-mcp"
      ]
    }
  }
}
```

Reload Cursor (`Cmd/Ctrl + Shift + P` → `Developer: Reload Window`).

</details>

<details>
<summary><b>Windsurf</b></summary>

Edit `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "seo-echo": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/canberkys/seo-echo-mcp",
        "seo-echo-mcp"
      ]
    }
  }
}
```

Restart Windsurf.

</details>

<details>
<summary><b>VS Code (GitHub Copilot)</b></summary>

Create `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "seo-echo": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/canberkys/seo-echo-mcp",
        "seo-echo-mcp"
      ]
    }
  }
}
```

Reload VS Code and confirm via the Copilot Chat settings.

</details>

<details>
<summary><b>Zed</b></summary>

Add to `~/.config/zed/settings.json`:

```json
{
  "context_servers": {
    "seo-echo": {
      "command": {
        "path": "uvx",
        "args": [
          "--from",
          "git+https://github.com/canberkys/seo-echo-mcp",
          "seo-echo-mcp"
        ]
      }
    }
  }
}
```

Reload Zed (`Cmd/Ctrl + Shift + P` → `zed: reload`).

</details>

> **Tip:** To pin a specific release add `@v0.4.0` (or any tag) to the git URL: `git+https://github.com/canberkys/seo-echo-mcp@v0.4.0`. To pull the latest commit after an update: run `uvx --refresh ...` once, then the IDE caches it again.

> **Verify:** regardless of IDE, try prompting `"analyze_site for myblog.com"` — if the MCP is wired up, your assistant will chain the tools automatically.

## API Reference

Every tool is `async def`. Realistic sample outputs live in [`examples/`](examples/).

### Research & strategy

**`analyze_site(url=None, urls=None, max_samples=12, cache_ttl=86400, bypass_cache=False) → SiteProfile`**
Crawl a blog and return its voice profile. Pass `url` for auto-discovery via sitemap/feed, or `urls=[...]` to skip discovery (useful for blocked/JS-rendered sites). Results are cached at `~/.cache/seo-echo-mcp/<domain>.json` for 24h by default — override with `SEO_ECHO_CACHE_DIR` env or `bypass_cache=True`. See [`examples/site_profile.json`](examples/site_profile.json).

**`analyze_competitors(keyword=None, urls=None, language="en", country="us", top_n=10) → CompetitorAnalysis`**
Fetch and structure top SERP results (or a given URL list). SERP provider order: Google CSE (if `GOOGLE_CSE_API_KEY` + `GOOGLE_CSE_ID` set) → DuckDuckGo HTML → Bing HTML.

**`detect_content_gaps(site_profile, competitor_analysis, min_coverage=2) → ContentGapReport`**
Topics competitors cover but your site doesn't, ranked by coverage count. See [`examples/content_gap_report.json`](examples/content_gap_report.json).

**`check_duplicates(proposed, site_profile, threshold=0.3) → DuplicateReport`**
Jaccard similarity over stopword-filtered tokens (stemmed for TR). Flags existing posts that overlap your proposed keyword/title and labels the verdict `safe` / `caution` / `duplicate`.

### Structure & metadata

**`suggest_titles(keyword, site_profile, competitor_analysis=None, count=10) → TitleSuggestions`**
10 ranked title candidates, style-matched to the site's H2 pattern. If competitors are provided, the most-common listicle N is honored (e.g. `Top 10 …` instead of hard-coded 7).

**`generate_meta_variations(keyword, title, language="en") → MetaVariations`**
5 meta descriptions across 5 angles (problem-solution, question, benefit, curiosity, action), all 140–160 chars.

**`generate_slug(title, language="en", max_length=60) → SlugResult`**
URL-safe slug with language-aware transliteration (`ı→i`, `ü→ue`, `ñ→n`, …), plus up to two shorter alternatives (stopword-stripped, truncated).

**`generate_outline(keyword, site_profile, competitor_analysis=None, target_word_count=None, new_category=None) → Outline`**
5–12 sections with unique H2s (language-specific), 3 title candidates, 3 meta descriptions, internal link targets, citation-research topic stubs. Rule-based. See [`examples/outline.json`](examples/outline.json).

**`generate_faq_section(keyword, language="en", competitor_analysis=None, count=5) → FaqSection`**
PAA-style FAQ markdown block + FAQPage JSON-LD. Question-shaped competitor H2s are folded in when available.

**`generate_schema_jsonld(schema_type, title, description, url, author_name, published_at, image_url=None, keywords=None, language="en") → SchemaJsonLd`**
Article / BlogPosting / HowTo / Review JSON-LD + ready-to-paste `<script>` snippet.

### Draft scaffolding & post-draft quality

**`prepare_draft_skeleton(outline, site_profile, target_keyword=None, slug=None, faq_section=None, schema_jsonld=None, selected_title_index=0, selected_meta_index=0, voice_overrides=None) → DraftSkeleton`**
Assembles the full markdown skeleton (frontmatter + `<!-- WRITE -->` directives per section + optional FAQ + JSON-LD). The host LLM fills each directive and saves the final `.md`. See [`examples/draft_skeleton.md`](examples/draft_skeleton.md).

**`audit_content(content_markdown, site_profile, target_keyword=None, target_meta_description=None, voice_overrides=None) → AuditReport`**
16 rule-based checks (word count, H2 format, em-dash, AI clichés, keyword density, heading hierarchy, image alt coverage, …). Score 0–100 with prioritized recommendations. See [`examples/audit_report.json`](examples/audit_report.json).

**`readability_report(content_markdown, language="en") → ReadabilityReport`**
Per-language formula (Flesch-EN, Ateşman-TR, Fernández-Huerta-ES, generic fallback) + passive-voice ratio for EN/TR/DE.

**`suggest_image_alts(content_markdown, target_keyword=None, language="en") → ImageAltReport`**
Flags missing/weak alt text per image and proposes replacements from the filename stem, the target keyword, and the nearest preceding paragraph. Alt template is language-aware.

## Content Creation Workflow with Claude Code

Because every tool is rule/template-based, the **host LLM (Claude) writes the prose** — the MCP just builds the scaffolding. A single prompt can chain all 14 tools:

> *"Analyze `myblog.com`, research competitors for `async python`, check if I already wrote about it, get a draft skeleton with FAQ + Article JSON-LD, fill the skeleton in my voice and save it as `content/async-python.md`, then audit + score readability."*

Claude will:

1. `analyze_site("myblog.com")` → `SiteProfile`
2. `analyze_competitors(keyword="async python")` → `CompetitorAnalysis`
3. `detect_content_gaps(site, competitors)` → topics you're missing
4. `check_duplicates("async python", site)` → safe/caution/duplicate
5. `suggest_titles("async python", site, competitors)` → 10 titles; picks one
6. `generate_outline("async python", site, competitors)` → `Outline`
7. `generate_faq_section("async python", "en", competitors)` → FAQ + JSON-LD
8. `generate_schema_jsonld("Article", ...)` → Article JSON-LD
9. `prepare_draft_skeleton(outline, site, faq, schema)` → markdown skeleton with `<!-- WRITE -->` directives
10. **Claude fills every directive** in your voice, respecting word count, addressing ("you"/"sen"/"vous"…), em-dash policy, etc.
11. Claude saves the filled markdown via its `Write` tool → `content/async-python.md`
12. `audit_content(draft, site, target_keyword)` → `AuditReport` (score + fixes)
13. `readability_report(draft, language)` → Flesch/Ateşman/Fernández-Huerta score + passive voice (EN/TR/DE)
14. `suggest_image_alts(draft, target_keyword)` → flags missing/weak alt text and proposes replacements

You end up with a publishable `.md` that matches your blog's voice, passes SEO checks, and has schema markup ready to paste into `<head>`.

## Usage example — minimal workflow

```
User:  "Analyze myblog.com, then outline a post about 'async python'."

Assistant (via MCP):
  1. analyze_site("myblog.com")              → SiteProfile
  2. analyze_competitors("async python")     → CompetitorAnalysis
  3. generate_outline(...)                   → Outline
  4. [Claude writes the draft from outline]
  5. audit_content(draft, site_profile,
                   target_keyword=...)       → AuditReport
```

## Contributing

Contributions welcome.

**Adding a language to AI cliché detection:**
edit `src/seo_echo_mcp/config/ai_cliches.py`, add your ISO 639-1 language code and a list of phrases, submit a PR.

**Adding outline templates for a new language:**
create `src/seo_echo_mcp/config/templates/<lang>.py` with `TITLE_TEMPLATES`, `META_TEMPLATES`, `H2_TEMPLATES`, and `CTA`, then add the code to `SUPPORTED` in `templates/loader.py`.

## Use as a Python library

The tools are plain async functions. You can import them and call them without an MCP host, e.g. from a Django management command, a CI step, or a notebook.

```python
import asyncio
from seo_echo_mcp.tools.analyze_site import analyze_site
from seo_echo_mcp.tools.generate_outline import generate_outline
from seo_echo_mcp.tools.audit_content import audit_content

async def main():
    profile = await analyze_site("myblog.com", max_samples=8)
    outline = await generate_outline("async python", profile)
    # (draft would be written by your prose source — LLM, human, template, …)
    draft_md = open("draft.md").read()
    report = await audit_content(draft_md, profile, target_keyword="async python")
    print(report.overall_score, report.recommendations)

asyncio.run(main())
```

Every tool returns a Pydantic model; call `.model_dump_json()` for JSON or `.model_dump()` for a plain dict. Inputs that are Pydantic models (e.g. `SiteProfile`) also accept dicts — Pydantic validates on the way in.

## Troubleshooting

**Tools don't show up in `/mcp`.** Confirm you picked the right scope: `--scope user` puts the registration in `~/.claude.json`, visible from any directory; `--scope local` is only visible in the directory where you ran the command. Run `claude mcp list` to see what's registered.

**`analyze_site` returns `Unable to reach URL`.** The target site may be blocking non-browser User-Agents or rate-limiting. Try passing an explicit post list via `urls=[...]` to skip sitemap discovery.

**`analyze_competitors` returns no results.** DuckDuckGo rate-limits aggressively. Set `GOOGLE_CSE_API_KEY` + `GOOGLE_CSE_ID` env vars to use Google Custom Search instead (best quality), or pass `urls=[...]` for a manual competitor list.

**Cache feels stale.** Clear `~/.cache/seo-echo-mcp/` or pass `bypass_cache=True` for a one-off fresh run. Override the path with `SEO_ECHO_CACHE_DIR=/tmp/seo-echo-cache`.

**Draft keeps using em-dashes / wrong tone.** Pass `voice_overrides={"em_dash_frequency": "never"}` (or any other `StyleProfile` field) to `prepare_draft_skeleton` and `audit_content`. See the "Overriding voice heuristics" section above.

**See more detail in IDE logs.** Set `SEO_ECHO_LOG_LEVEL=DEBUG` on the IDE's MCP command; every tool emits start/finish milestones to stderr (stdout is reserved for the MCP stdio protocol).

## What this MCP does NOT do

Expectation management:

- **It does not write prose.** Every tool is rule/template-based. The host LLM (Claude / Cursor / etc.) generates the actual text after consuming the outline + skeleton.
- **It does not call external LLM APIs** from inside any tool. No hidden OpenAI / Anthropic / Gemini calls. No API keys required by default (optional Google CSE only).
- **It does not store credentials.** The only disk write is an opt-in cache at `~/.cache/seo-echo-mcp/`.
- **It is not a keyword research tool.** For search volume, SERP CTR, backlinks, etc., integrate a dedicated tool (e.g. Ahrefs, Semrush) — `seo-echo-mcp` focuses on voice + structure.
- **It is not a plagiarism or fact-checker.** Audit checks style and SEO hygiene; it cannot verify claims.

## Roadmap

- [x] v0.2 — Content creator expansion (9 new tools, 13 total)
- [x] v0.3 — Manual URL list input for `analyze_site`, persistent cache, `suggest_image_alts`, TR/DE passive voice
- [x] v0.4 — Language-aware fallbacks (outline + image alts), TR stemmer, stratified sampling, pronoun families, cache path hardening, CONTRIBUTING/SECURITY/CODE_OF_CONDUCT, examples/
- [ ] v0.5 — Multi-site profile comparison
- [ ] v0.5 — Semantic similarity in `check_duplicates` (TF-IDF / embeddings)

## License

MIT — see [LICENSE](LICENSE).
