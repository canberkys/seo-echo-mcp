# Registry submission checklist

This doc tracks where `seo-echo-mcp` is listed in public MCP registries and exactly what to do to submit where it isn't yet. Treat each section as a copy-pasteable PR / form template.

## Status

| Registry | State | Notes |
|----------|-------|-------|
| [Smithery](https://smithery.ai) | Auto-discoverable | `smithery.yaml` at repo root |
| [Glama](https://glama.ai/mcp) | Auto-discoverable | `glama.json` at repo root; Glama crawls GitHub topics `mcp-server` + `mcp` |
| [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | Needs PR | Add an entry under the right category |
| [michaellatman/mcp-get](https://github.com/michaellatman/mcp-get) | Needs PR | Add `packages/seo-echo-mcp/` entry |
| MCP Servers (official) | Needs form | Submit at https://modelcontextprotocol.io/servers if/when listing exists |

## awesome-mcp-servers PR

1. Fork https://github.com/punkpeye/awesome-mcp-servers
2. Find the "Content Creation" / "Writing" / "SEO" section (or add under "Other / Miscellaneous").
3. Add this line alphabetically inside that section:

   ```markdown
   - [seo-echo-mcp](https://github.com/canberkys/seo-echo-mcp) - Voice-preserving SEO content MCP server. 14 rule-based tools for analyzing a blog's voice, generating outlines, FAQ + JSON-LD schema, and auditing drafts. Language-agnostic, no external LLM calls.
   ```

4. PR title: `Add seo-echo-mcp`
5. PR body:

   ```markdown
   ### What it is
   14-tool MCP server for voice-preserving SEO content. Runs in Claude Code / Desktop / Cursor / Windsurf / VS Code / Zed.

   ### Why it's useful
   - Rule/template-based — zero external LLM API calls
   - Language-agnostic (EN, TR, ES, FR, DE templates ship, others fall back gracefully)
   - Full pipeline: site analysis → competitor research → outline + FAQ + schema → draft skeleton → audit + readability + image-alt

   ### License
   MIT
   ```

## mcp-get PR

Format has shifted a few times; check current CONTRIBUTING.md. As of April 2026 the format is TS entry in `packages/`:

```typescript
// packages/seo-echo-mcp/package.ts
export default {
  name: "seo-echo-mcp",
  description: "Voice-preserving SEO content MCP — 14 rule-based tools, language-agnostic",
  vendor: "canberkys",
  sourceUrl: "https://github.com/canberkys/seo-echo-mcp",
  homepage: "https://github.com/canberkys/seo-echo-mcp",
  license: "MIT",
  runtime: "python",
  install: {
    command: "uvx",
    args: ["--from", "git+https://github.com/canberkys/seo-echo-mcp", "seo-echo-mcp"],
  },
};
```

PR title: `feat: add seo-echo-mcp`. Body: same as awesome-mcp-servers above.

## Announcement posts (optional, low-friction)

- **r/ClaudeAI** — weekly "what did you build" thread
- **r/LLMDevs** — weekly showcase thread
- **Hacker News** — "Show HN" submission (one shot, best on weekday mornings ET)
- **LinkedIn** — personal post with 14-tool diagram + GIF if captured
- **Twitter/X** — use the 2-3 tweet templates we already prepared

## After any listing is approved

1. Add a badge to the top of `README.md` (Smithery / Glama provide badge URLs).
2. Note the listing URL in this table.
3. Optionally, add a `Status` checkmark in the main `README.md` "Community" section once one exists.
