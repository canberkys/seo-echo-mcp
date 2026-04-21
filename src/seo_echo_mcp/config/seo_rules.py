"""Numeric SEO thresholds used by audit_content and generate_outline."""

from __future__ import annotations

# Keyword density target (fraction of total words)
KEYWORD_DENSITY_MIN = 0.005
KEYWORD_DENSITY_MAX = 0.02

# Meta description bounds (characters)
META_DESC_MIN = 140
META_DESC_MAX = 160

# Minimum link targets
MIN_INTERNAL_LINKS = 3
MIN_EXTERNAL_LINKS = 3

# Word-count tolerance vs site average
WORD_COUNT_TOLERANCE = 0.25  # ±25%

# Scoring weights
SEVERITY_WEIGHTS: dict[str, int] = {"error": 10, "warning": 3, "info": 1}

# Reading speed (words per minute)
READING_WPM = 200
