"""Heuristic writing-style analysis.

Language-aware pronoun detection lets us catch addressing ("sen"/"siz" in TR,
"tu"/"vous" in FR, "du"/"Sie" in DE, etc.) without hardcoding English.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Literal

from seo_echo_mcp.schemas import StyleProfile

# Per-language 2nd-person pronoun candidates
PRONOUNS: dict[str, list[str]] = {
    "tr": ["sen", "siz", "senin", "sizin", "sana", "size"],
    "en": ["you", "your", "yours"],
    "es": ["tú", "usted", "ustedes", "vosotros"],
    "fr": ["tu", "vous", "ton", "votre"],
    "de": ["du", "sie", "ihr", "dein", "ihre"],
    "it": ["tu", "voi", "lei", "tuo", "vostro"],
    "pt": ["tu", "você", "vocês"],
}

# Imperative verb markers per language (suffixes/heuristics)
IMPERATIVE_HINTS: dict[str, list[str]] = {
    "tr": ["yap", "öğren", "keşfet", "dene", "oku", "izle"],
    "en": ["build", "learn", "discover", "try", "read", "watch", "get", "master"],
    "es": ["aprende", "descubre", "prueba", "lee"],
    "fr": ["apprenez", "découvrez", "essayez", "lisez"],
    "de": ["lernen", "entdecken", "versuchen", "lesen"],
}

TONE_JARGON_WORDS = {
    "api",
    "sdk",
    "async",
    "kubernetes",
    "docker",
    "serverless",
    "pipeline",
    "schema",
    "framework",
    "algorithm",
}


def analyze_style(texts: list[str], titles: list[list[str]], language: str) -> StyleProfile:
    """Return a StyleProfile for a batch of sampled posts.

    `texts` is one body string per post; `titles` is the list of h2 strings
    per post (same order as `texts`).
    """
    all_text = "\n\n".join(texts)
    wc = _word_count(all_text)
    post_word_counts = [_word_count(t) for t in texts]
    avg_wc = int(sum(post_word_counts) / max(len(post_word_counts), 1))

    tone = _tone(all_text)
    addressing = _addressing(all_text, language)
    h2s = [h for sub in titles for h in sub]
    h2_pattern = _h2_pattern(h2s, language)
    em_dash_freq = _em_dash_frequency(all_text, wc)
    avg_sentence = _avg_sentence_words(all_text)
    avg_para = _avg_paragraph_sentences(texts)
    uses_lists = _uses_lists(texts)
    uses_code = _uses_code(texts)

    return StyleProfile(
        average_word_count=avg_wc,
        tone=tone,
        addressing=addressing,
        h2_pattern=h2_pattern,
        uses_lists=uses_lists,
        uses_code_blocks=uses_code,
        avg_paragraph_sentences=round(avg_para, 2),
        em_dash_frequency=em_dash_freq,
        avg_sentence_words=round(avg_sentence, 2),
    )


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _tone(
    text: str,
) -> Literal["formal", "informal", "technical", "conversational", "journalistic", "mixed"]:
    tokens = re.findall(r"[\w']+", text.lower())
    if not tokens:
        return "mixed"
    jargon_ratio = sum(1 for t in tokens if t in TONE_JARGON_WORDS) / len(tokens)
    sentence_lengths = [len(s.split()) for s in re.split(r"[.!?]+", text) if s.strip()]
    avg_sl = sum(sentence_lengths) / max(len(sentence_lengths), 1)
    contractions = len(re.findall(r"\b\w+['’]\w+\b", text))
    q_marks = text.count("?")

    if jargon_ratio > 0.01:
        return "technical"
    if contractions > 20 and q_marks > 5:
        return "conversational"
    if avg_sl < 14 and q_marks > 3:
        return "informal"
    if avg_sl > 22:
        return "formal"
    if 14 <= avg_sl <= 20 and q_marks <= 2:
        return "journalistic"
    return "mixed"


def _addressing(text: str, language: str) -> str:
    lowered = text.lower()
    candidates = PRONOUNS.get(language, PRONOUNS["en"])
    counts: Counter[str] = Counter()
    for p in candidates:
        counts[p] = len(re.findall(rf"\b{re.escape(p)}\b", lowered))
    if not counts or sum(counts.values()) == 0:
        return "impersonal"
    top, _ = counts.most_common(1)[0]
    return top


def _h2_pattern(
    h2s: list[str], language: str
) -> Literal["question", "statement", "imperative", "mixed"]:
    if not h2s:
        return "mixed"
    total = len(h2s)
    q = sum(1 for h in h2s if h.rstrip().endswith("?"))
    imp_hints = IMPERATIVE_HINTS.get(language, IMPERATIVE_HINTS["en"])
    imp = sum(
        1
        for h in h2s
        if any(h.lower().startswith(hint + " ") or h.lower() == hint for hint in imp_hints)
    )
    if q / total > 0.5:
        return "question"
    if imp / total > 0.4:
        return "imperative"
    if q / total < 0.15 and imp / total < 0.15:
        return "statement"
    return "mixed"


def _em_dash_frequency(
    text: str, word_count: int
) -> Literal["frequent", "occasional", "rare", "never"]:
    count = text.count("—")
    if count == 0:
        return "never"
    if word_count == 0:
        return "rare"
    per_thousand = count / (word_count / 1000)
    if per_thousand > 5:
        return "frequent"
    if per_thousand > 1:
        return "occasional"
    return "rare"


def _avg_sentence_words(text: str) -> float:
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sentences:
        return 0.0
    lengths = [len(re.findall(r"\S+", s)) for s in sentences]
    return sum(lengths) / len(lengths)


def _avg_paragraph_sentences(texts: list[str]) -> float:
    totals: list[float] = []
    for t in texts:
        # Trafilatura's txt output joins paragraphs with single newlines; fall
        # back to single-newline splitting when the double-newline delimiter
        # is absent so each paragraph is counted individually.
        if "\n\n" in t:
            paragraphs = [p for p in t.split("\n\n") if p.strip()]
        else:
            paragraphs = [p for p in t.split("\n") if p.strip()]
        for p in paragraphs:
            sents = [s for s in re.split(r"[.!?]+", p) if s.strip()]
            if sents:
                totals.append(len(sents))
    if not totals:
        return 0.0
    return sum(totals) / len(totals)


def _uses_lists(texts: list[str]) -> bool:
    hits = sum(1 for t in texts if re.search(r"^\s*[-*•]\s", t, re.MULTILINE))
    return hits >= max(1, len(texts) // 3)


def _uses_code(texts: list[str]) -> bool:
    hits = sum(1 for t in texts if "```" in t or re.search(r"^\s{4}[\w#]", t, re.MULTILINE))
    return hits >= max(1, len(texts) // 4)
