"""Resolve outline templates by language code, falling back to English."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType

SUPPORTED = ("en", "tr", "es", "fr", "de")


def load(language: str) -> ModuleType:
    """Return the template module for `language`, falling back to English."""
    code = language.lower()
    if code not in SUPPORTED:
        code = "en"
    return import_module(f"seo_echo_mcp.config.templates.{code}")
