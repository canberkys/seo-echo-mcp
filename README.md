# seo-echo-mcp

**Voice-preserving SEO content MCP server — language-agnostic.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![PyPI](https://img.shields.io/pypi/v/seo-echo-mcp)](https://pypi.org/project/seo-echo-mcp/)

[Features](#features) • [Installation](#installation) • [IDE Setup](#ide-setup) • [API Reference](#api-reference) • [Contributing](#contributing)

---

## What is this?

Most SEO MCPs give you keyword data. **seo-echo-mcp is different:** it reads your existing blog, extracts your writing voice, and makes sure new SEO content matches that voice — in any language.

Think of it as giving your LLM assistant a "style mirror" for your content.

## Features

13 tools covering the full pipeline from site analysis through publish-ready draft + schema. Every tool is rule/template-based — **no external LLM/API calls**.

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
| `readability_report` | Per-language readability (Flesch-EN, Ateşman-TR, Fernández-Huerta-ES, generic fallback) |

### Overriding voice heuristics

`analyze_site` measures the voice of your **existing** posts. If your editorial preference differs — e.g. "my blog uses em-dashes occasionally but I don't want them in new drafts" — pass `voice_overrides` to `prepare_draft_skeleton` and `audit_content`:

```python
voice_overrides = {"em_dash_frequency": "never"}
```

Any `StyleProfile` field can be overridden this way (`em_dash_frequency`, `addressing`, `tone`, `average_word_count`, …). The site profile itself is not mutated — the override only affects that single tool call.

## Language support

Works with **any language** that has an ISO 639-1 code. Built-in AI cliché detection for: Turkish, English, Spanish, French, German (contributions welcome for more).

## Installation

### Via PyPI (recommended)

```bash
pip install seo-echo-mcp
# or
uv pip install seo-echo-mcp
```

### Via uvx (no install)

Configure your IDE to run `uvx seo-echo-mcp` directly — no manual install needed.

## IDE Setup

### Claude Code

```bash
claude mcp add seo-echo --scope user -- uvx seo-echo-mcp
```

### Claude Desktop

`claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "seo-echo": {
      "command": "uvx",
      "args": ["seo-echo-mcp"]
    }
  }
}
```

### Cursor

`.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "seo-echo": {
      "command": "uvx",
      "args": ["seo-echo-mcp"]
    }
  }
}
```

### Windsurf

`~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "seo-echo": {
      "command": "uvx",
      "args": ["seo-echo-mcp"]
    }
  }
}
```

### VS Code (GitHub Copilot)

`.vscode/mcp.json`:

```json
{
  "servers": {
    "seo-echo": {
      "command": "uvx",
      "args": ["seo-echo-mcp"]
    }
  }
}
```

### Zed

`~/.config/zed/settings.json`:

```json
{
  "context_servers": {
    "seo-echo": {
      "command": {
        "path": "uvx",
        "args": ["seo-echo-mcp"]
      }
    }
  }
}
```

## API Reference

### `analyze_site(url, max_samples=12)`

Crawls `url`, samples up to `max_samples` posts, and returns a `SiteProfile`:

```json
{
  "domain": "myblog.com",
  "language": "en",
  "language_confidence": "high",
  "categories": ["Guides", "Tutorials"],
  "topics": ["python", "testing", "async"],
  "style": {
    "average_word_count": 1400,
    "tone": "conversational",
    "addressing": "you",
    "h2_pattern": "question",
    "em_dash_frequency": "rare"
  },
  "existing_posts": [ ... ]
}
```

### `analyze_competitors(keyword=None, urls=None, language, country, top_n=10)`

Analyzes competitor content. Either `keyword` (for SERP search) or `urls` (direct list) is required. Returns `CompetitorAnalysis` with per-page structure and aggregate insights.

SERP providers, in order of preference:

1. **Google Custom Search** (if `GOOGLE_CSE_API_KEY` + `GOOGLE_CSE_ID` env vars set)
2. **DuckDuckGo HTML** (default)
3. **Bing HTML** (fallback if DuckDuckGo is rate-limited)

### `generate_outline(keyword, site_profile, competitor_analysis=None, target_word_count=None, new_category=None)`

Produces an `Outline` with 5–12 sections, 3 title candidates, 3 meta descriptions, recommended internal link targets, and citation-research topic stubs. Rule-based — no LLM calls inside the tool.

### `audit_content(content_markdown, site_profile, target_keyword=None, target_meta_description=None)`

Runs 16 rule-based checks (word count, H2 format, em-dash usage, AI clichés, keyword density, heading hierarchy, image alt coverage, …). Returns an `AuditReport` with an overall score 0–100, per-check results, and prioritized recommendations.

## Content Creation Workflow with Claude Code

Because every tool is rule/template-based, the **host LLM (Claude) writes the prose** — the MCP just builds the scaffolding. A single prompt can chain all 13 tools:

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
13. `readability_report(draft, language)` → Flesch/Ateşman/Fernández-Huerta score

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

## Roadmap

- [x] v0.2 — Content creator expansion (9 new tools, 13 total)
- [ ] v0.3 — Manual URL list input for `analyze_site`
- [ ] v0.3 — Persistent cache for site profiles
- [ ] v0.3 — Image alt-text suggestion tool
- [ ] v0.4 — Multi-site profile comparison

## License

MIT — see [LICENSE](LICENSE).

## Credits

Inspired by [egebese/seo-research-mcp](https://github.com/egebese/seo-research-mcp) (keyword data) and similar community MCP projects.
