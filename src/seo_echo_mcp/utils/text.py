"""Shared markdown/text helpers used by multiple tools.

These were originally private helpers inside `audit_content`; they are now
reused by `readability_report` and `prepare_draft_skeleton`.
"""

from __future__ import annotations

import re


def strip_frontmatter(md: str) -> str:
    """Return markdown body with leading `---...---` YAML frontmatter removed."""
    if md.startswith("---"):
        end = md.find("\n---", 3)
        if end != -1:
            return md[end + 4 :].lstrip("\n")
    return md


def markdown_to_plain(md: str) -> str:
    """Strip markdown formatting to approximate plain prose for NLP heuristics."""
    text = re.sub(r"```[\s\S]*?```", "", md)
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<!--[\s\S]*?-->", "", text)  # also strip HTML comments (skeleton directives)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_>~]", "", text)
    return text


def split_headings(md: str) -> tuple[str, list[str], list[str]]:
    """Return (h1, h2_list, h3_list) from a markdown body."""
    h1 = ""
    h2s: list[str] = []
    h3s: list[str] = []
    for line in md.splitlines():
        m = re.match(r"^(#{1,3})\s+(.*?)\s*$", line)
        if not m:
            continue
        level, text = m.group(1), m.group(2).strip()
        if level == "#" and not h1:
            h1 = text
        elif level == "##":
            h2s.append(text)
        elif level == "###":
            h3s.append(text)
    return h1, h2s, h3s


def tokenize_words(text: str) -> list[str]:
    """Return lowercased word tokens (length >= 1)."""
    return re.findall(r"[\w']+", text.lower())


def count_syllables_en(word: str) -> int:
    """Rough English syllable counter — vowel group heuristic.

    Accurate enough for Flesch-style formulas on short blog posts.
    """
    word = word.lower()
    if not word:
        return 0
    groups = re.findall(r"[aeiouy]+", word)
    count = len(groups)
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


# Turkish inflectional suffixes we can strip without heavy morphology.
# Ordered longest-first so we don't trim a shorter prefix of a longer suffix.
# The apostrophe-prefixed variants catch "VMware'ın", "snapshot'ları", etc.
_TR_SUFFIXES = (
    "'lardan",
    "'lerden",
    "'larla",
    "'lerle",
    "'lardır",
    "'lerdir",
    "'ların",
    "'lerin",
    "'ları",
    "'leri",
    "'lar",
    "'ler",
    "'daki",
    "'deki",
    "'dan",
    "'den",
    "'tan",
    "'ten",
    "'nın",
    "'nin",
    "'nun",
    "'nün",
    "'ın",
    "'in",
    "'un",
    "'ün",
    "'la",
    "'le",
    "'ya",
    "'ye",
    "'na",
    "'ne",
    "'ı",
    "'i",
    "'u",
    "'ü",
    "'a",
    "'e",
    "'s",
    "lardan",
    "lerden",
    "larla",
    "lerle",
    "lardır",
    "lerdir",
    "ların",
    "lerin",
    "larda",
    "lerde",
    "larda",
    "lerde",
    "dan",
    "den",
    "tan",
    "ten",
    "ları",
    "leri",
    "lar",
    "ler",
    "nın",
    "nin",
    "nun",
    "nün",
    "ın",
    "in",
    "un",
    "ün",
    "la",
    "le",
    "ya",
    "ye",
    "na",
    "ne",
    "da",
    "de",
    "ta",
    "te",
    "ı",
    "i",
    "u",
    "ü",
    "a",
    "e",
)


def stem_tr(word: str) -> str:
    """Return an approximate Turkish stem by stripping a common inflection.

    Heuristic-only — does not apply vowel harmony checks or morphological
    analysis. Good enough for Jaccard-style similarity where we want
    "snapshot'ları" and "snapshot" to collapse to the same token.

    Minimum stem length is 3 chars; suffixes that would leave a shorter stem
    are not applied.
    """
    lowered = word.lower()
    if len(lowered) <= 3:
        return lowered
    for suffix in _TR_SUFFIXES:
        if lowered.endswith(suffix) and len(lowered) - len(suffix) >= 3:
            return lowered[: -len(suffix)]
    return lowered
