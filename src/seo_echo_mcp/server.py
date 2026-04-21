"""FastMCP entry point for seo-echo-mcp.

Registers the four public tools and exposes `main()` as the stdio CLI entry.

Logging is configured here to write to **stderr only** — stdout is reserved for
the MCP stdio protocol. Level can be overridden via the `SEO_ECHO_LOG_LEVEL`
environment variable (default `INFO`).
"""

from __future__ import annotations

import logging
import os
import sys

from fastmcp import FastMCP

from seo_echo_mcp.tools.analyze_competitors import analyze_competitors
from seo_echo_mcp.tools.analyze_site import analyze_site
from seo_echo_mcp.tools.audit_content import audit_content
from seo_echo_mcp.tools.check_duplicates import check_duplicates
from seo_echo_mcp.tools.detect_content_gaps import detect_content_gaps
from seo_echo_mcp.tools.generate_faq_section import generate_faq_section
from seo_echo_mcp.tools.generate_meta_variations import generate_meta_variations
from seo_echo_mcp.tools.generate_outline import generate_outline
from seo_echo_mcp.tools.generate_schema_jsonld import generate_schema_jsonld
from seo_echo_mcp.tools.generate_slug import generate_slug
from seo_echo_mcp.tools.prepare_draft_skeleton import prepare_draft_skeleton
from seo_echo_mcp.tools.readability_report import readability_report
from seo_echo_mcp.tools.suggest_image_alts import suggest_image_alts
from seo_echo_mcp.tools.suggest_titles import suggest_titles


def _configure_logging() -> None:
    level_name = os.environ.get("SEO_ECHO_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger("seo_echo_mcp")
    root.setLevel(level)
    # Replace existing handlers so repeated imports don't stack them.
    root.handlers = [handler]
    root.propagate = False


_configure_logging()

mcp = FastMCP(
    name="seo-echo-mcp",
    instructions=(
        "Voice-preserving SEO content workflow. Typical chain: "
        "analyze_site → analyze_competitors → detect_content_gaps → check_duplicates → "
        "suggest_titles → generate_outline → generate_faq_section → generate_schema_jsonld → "
        "prepare_draft_skeleton → [host LLM fills the skeleton and saves the .md] → "
        "audit_content → readability_report. generate_slug and generate_meta_variations are "
        "on-demand helpers. No external LLM/API calls are made inside these tools."
    ),
)

# Research + strategy
mcp.tool(analyze_site)
mcp.tool(analyze_competitors)
mcp.tool(detect_content_gaps)
mcp.tool(check_duplicates)

# Structure + metadata
mcp.tool(suggest_titles)
mcp.tool(generate_meta_variations)
mcp.tool(generate_slug)
mcp.tool(generate_outline)
mcp.tool(generate_faq_section)
mcp.tool(generate_schema_jsonld)

# Draft scaffolding (hand-off to host LLM)
mcp.tool(prepare_draft_skeleton)

# Post-draft quality
mcp.tool(audit_content)
mcp.tool(readability_report)
mcp.tool(suggest_image_alts)


def main() -> None:
    """Run the MCP server over stdio (default transport for IDE hosts)."""
    mcp.run()


if __name__ == "__main__":
    main()
