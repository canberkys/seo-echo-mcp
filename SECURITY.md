# Security Policy

## Supported versions

The latest `0.x` minor release is the only supported version. Older 0.x releases do not receive security patches — upgrade to the current release.

| Version | Supported |
|---------|-----------|
| 0.4.x   | ✓ |
| 0.3.x   | ✗ |
| 0.2.x   | ✗ |
| < 0.2   | ✗ |

## Reporting a vulnerability

**Please do not open a public GitHub issue for security reports.**

Use one of these channels instead:

- **Preferred:** [Open a private security advisory](https://github.com/canberkys/seo-echo-mcp/security/advisories/new) — only maintainers see it.
- **Alternative:** email **kayit@canberkki.com** with the subject `[seo-echo-mcp][security]`.

Please include:

- Affected version (e.g. `v0.4.0`) or commit SHA.
- A minimal reproduction (tool call + input that triggers the issue).
- Impact assessment — data exposure, RCE, DoS, etc.
- Any known mitigation.

## What we consider in scope

- **Path traversal / arbitrary file write** via cache keys, slug generation, or any tool that touches disk.
- **SSRF** via `analyze_site` / `analyze_competitors` if URLs bypass sanitization.
- **Memory exhaustion** (unbounded response sizes, unbounded iteration).
- **Prompt injection** in tool output that a host LLM would blindly execute (e.g. a draft skeleton containing crafted `<!-- WRITE -->` directives that manipulate the LLM).
- **Dependency vulnerabilities** flagged by Dependabot.

## Out of scope

- Rate limiting of outbound HTTP (DuckDuckGo / Bing scraping is best-effort; use Google CSE via env vars for production).
- Hardening of the MCP host itself — that is the IDE's responsibility.
- Output quality (false positives in heuristics) — file those as regular issues.

## Response target

- Acknowledge within 72 hours.
- Assess severity and draft a fix within 7 days for `HIGH`/`CRITICAL`, 30 days for `LOW`/`MEDIUM`.
- Coordinate disclosure timeline with the reporter before publishing a patch release.
