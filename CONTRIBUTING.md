# Contributing to seo-echo-mcp

Thanks for your interest. This project is language-agnostic by design — most useful contributions come from **adding a new language** or **a new tool**. Everything below assumes you already have [`uv`](https://docs.astral.sh/uv/) installed.

## Local setup

```bash
git clone https://github.com/canberkys/seo-echo-mcp
cd seo-echo-mcp
uv sync --extra dev
uv run ruff check
uv run ruff format --check
uv run pytest -q
```

CI runs on Python 3.10–3.13. `ruff check`, `ruff format --check`, and `pytest` all need to pass.

## Adding a language

Three files, ~10 minutes. Example: adding Italian (`it`).

1. **`src/seo_echo_mcp/config/ai_cliches.py`** — add an `"it"` key to `AI_CLICHES` with 10–20 lowercase cliché phrases common in Italian blog/marketing copy.
2. **`src/seo_echo_mcp/config/templates/it.py`** — copy `en.py` as a starting point and translate the four top-level dicts: `TITLE_TEMPLATES`, `META_TEMPLATES`, `H2_TEMPLATES`, `META_ANGLES`, `FAQ_QUESTION_TEMPLATES`, `TITLE_VARIANT_TEMPLATES`, plus the `CTA` string.
3. **`src/seo_echo_mcp/config/templates/loader.py`** — add `"it"` to the `SUPPORTED` tuple.

Optional but welcome:

- **Slug transliteration** — if the language has diacritics, add an entry to `TRANSLITERATE` in `config/slug_rules.py`.
- **Stopwords for slugs** — add the language to `STOPWORDS` in the same file.
- **Readability formula** — if a published formula exists (e.g. Flesch-Szigriszt for Spanish), add a branch in `tools/readability_report.py::_score()` and a new `formula_used` value.
- **Passive voice** — add a regex to `_PASSIVE_PATTERNS` in `readability_report.py`.

## Adding a tool

1. Define input/output models in `src/seo_echo_mcp/schemas.py` (Pydantic `BaseModel`).
2. Create `src/seo_echo_mcp/tools/<tool_name>.py` with an async function of the same name. Keep the tool rule/template-based — **no external LLM or paid API calls**.
3. Register in `src/seo_echo_mcp/server.py`: add an import and `mcp.tool(<tool_name>)` line.
4. Write at least two smoke tests under `tests/test_<tool_name>.py`.
5. Document in `README.md` under the appropriate "Features" sub-table.
6. Add an entry to the `[Unreleased]` section of `CHANGELOG.md`.

## Code conventions

- **Stdio protocol is sacred**: never write to stdout from tool code. Use `logging.getLogger(__name__).info(...)` — the root logger is configured to stderr in `server.py`.
- **Language-agnostic**: hardcoded English strings in tool logic or Pydantic `Literal` values are fine for *schemas*, but user-facing output (suggestions, directives) must flow through `config/templates/<lang>.py`.
- **Async by default**: every tool signature is `async def`. Use `httpx.AsyncClient` for HTTP.
- **No state on disk** except the opt-in cache in `analyze_site`. All other tools are stateless.
- **Ruff is authoritative**: `uv run ruff format` before committing. The CI `ruff format --check` step will fail on unformatted code.

## Pull requests

- Branch from `main`.
- Keep PRs focused — one tool or one language per PR.
- Fill in the PR template checklist.
- Link to an issue if one exists.

## Reporting bugs

Use the "Bug report" issue template. If the bug is in a tool's output for a specific site, include:

- The tool call (inputs)
- Expected vs actual output (trim long `SiteProfile` JSON to the relevant fields)
- Language of the site if not English
- Whether you're using `uvx --from git+...` or a local clone
