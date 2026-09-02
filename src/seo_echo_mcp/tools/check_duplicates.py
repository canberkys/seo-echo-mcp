"""check_duplicates: flag existing posts that overlap with a proposed keyword/title."""

from __future__ import annotations

import logging
import math
import re
from collections import Counter
from typing import Literal

from seo_echo_mcp.schemas import DuplicateMatch, DuplicateReport, SiteProfile
from seo_echo_mcp.utils.text import stem_tr

logger = logging.getLogger(__name__)

_STOP = {
    # English
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "for",
    "with",
    "in",
    "on",
    "what",
    "how",
    "why",
    "when",
    "where",
    "which",
    "who",
    # Turkish — include common question/connective words so they don't
    # dominate Jaccard scores on short titles.
    "ve",
    "ile",
    "bir",
    "bu",
    "şu",
    "için",
    "olan",
    "gibi",
    "kadar",
    "nedir",
    "nasıl",
    "nas",
    "neden",
    "nerede",
    "niçin",
    "hangi",
    "hangisi",
    "hakkınd",
    "hakkında",
    "yönetim",
    "ilgili",
    # Spanish
    "el",
    "la",
    "los",
    "las",
    "de",
    "del",
    "y",
    "un",
    "una",
    "que",
    # French
    "le",
    "les",
    "du",
    "des",
    "et",
    "une",
    "qui",
    "quoi",
    # German
    "der",
    "die",
    "das",
    "und",
    "ein",
    "eine",
    "wer",
    "was",
}


async def check_duplicates(
    proposed: str,
    site_profile: SiteProfile,
    threshold: float = 0.3,
) -> DuplicateReport:
    """Detect whether the proposed keyword/title overlaps with existing posts.

    Uses TF-IDF cosine similarity over stopword-filtered, optionally stemmed
    tokens. Rare/distinctive terms (e.g. product names, technical jargon) are
    upweighted, so a single shared rare term scores higher than many shared
    common words — unlike Jaccard which treats all tokens equally.

    For Turkish sites, tokens are stemmed with a simple suffix trimmer so
    "snapshot'ları" and "snapshot" collapse to the same token.

    Args:
        proposed: Proposed keyword or title for the new piece.
        site_profile: SiteProfile from analyze_site (uses `existing_posts`).
        threshold: Minimum cosine similarity to flag (default 0.30).

    Returns:
        DuplicateReport with matches, scores, and an overall verdict.
    """
    if not proposed or not proposed.strip():
        raise ValueError("`proposed` must be a non-empty string.")
    language = site_profile.language
    logger.info(
        "check_duplicates proposed=%r lang=%s existing=%d",
        proposed,
        language,
        len(site_profile.existing_posts),
    )

    # Build corpus: each document is title + snippet tokens (ordered list for TF).
    corpus_docs: list[list[str]] = []
    corpus_posts = []
    for post in site_profile.existing_posts:
        tokens = _tokenize_list(f"{post.title} {post.snippet}", language)
        if tokens:
            corpus_docs.append(tokens)
            corpus_posts.append(post)

    proposed_tokens = _tokenize_list(proposed, language)
    if not proposed_tokens or not corpus_docs:
        return DuplicateReport(proposed=proposed, matches=[], verdict="safe")

    # IDF over corpus (sklearn smooth variant: log((N+1)/(df+1))+1).
    idf = _compute_idf(corpus_docs)

    proposed_vec = _tfidf_vector(proposed_tokens, idf)
    matches: list[DuplicateMatch] = []
    for post, doc_tokens in zip(corpus_posts, corpus_docs):
        doc_vec = _tfidf_vector(doc_tokens, idf)
        score = _cosine(proposed_vec, doc_vec)
        if score >= threshold:
            matches.append(
                DuplicateMatch(
                    existing_url=post.url,
                    existing_title=post.title,
                    overlap_score=round(score, 3),
                    reason=_reason(score),
                )
            )
    matches.sort(key=lambda m: -m.overlap_score)
    verdict: Literal["safe", "caution", "duplicate"] = _verdict(matches)
    return DuplicateReport(proposed=proposed, matches=matches, verdict=verdict)


def _tokenize_list(text: str, language: str = "en") -> list[str]:
    """Return an ordered token list (with repetition) for TF computation."""
    raw = re.findall(r"[\w']{3,}", text.lower())
    stop = _STOP
    if language == "tr":
        return [stem_tr(t) for t in raw if stem_tr(t) not in stop]
    return [t for t in raw if t not in stop]


def _tokenize(text: str, language: str = "en") -> set[str]:
    return set(_tokenize_list(text, language))


def _compute_idf(corpus: list[list[str]]) -> dict[str, float]:
    N = len(corpus)
    df: dict[str, int] = {}
    for doc in corpus:
        for term in set(doc):
            df[term] = df.get(term, 0) + 1
    return {term: math.log((N + 1) / (count + 1)) + 1.0 for term, count in df.items()}


def _tfidf_vector(tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
    if not tokens:
        return {}
    tf = Counter(tokens)
    total = len(tokens)
    return {term: (count / total) * idf.get(term, 1.0) for term, count in tf.items()}


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(a.get(t, 0.0) * v for t, v in b.items())
    mag_a = math.sqrt(sum(v * v for v in a.values()))
    mag_b = math.sqrt(sum(v * v for v in b.values()))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)


def _reason(score: float) -> str:
    if score >= 0.6:
        return "Very high token overlap — likely covers the same topic."
    if score >= 0.45:
        return "High overlap — merge or repurpose rather than create a new post."
    return "Moderate overlap — ensure the angle is distinct."


def _verdict(matches: list[DuplicateMatch]) -> Literal["safe", "caution", "duplicate"]:
    if not matches:
        return "safe"
    top = matches[0].overlap_score
    if top >= 0.6:
        return "duplicate"
    if top >= 0.45:
        return "caution"
    return "caution"
