"""score_title_clickability: heuristic CTR scoring for title candidates."""

from __future__ import annotations

import logging
import re

from seo_echo_mcp.schemas import TitleClickabilityItem, TitleClickabilityReport

logger = logging.getLogger(__name__)

_SERP_SAFE_LIMIT = 60
_OPTIMAL_MIN = 40
_OPTIMAL_MAX = 60

# Language-specific power words that correlate with higher CTR.
_POWER_WORDS: dict[str, set[str]] = {
    "en": {
        "free", "secret", "ultimate", "proven", "hack", "hacks", "best", "top",
        "easy", "simple", "complete", "guide", "tips", "tricks", "mistake",
        "mistakes", "avoid", "boost", "improve", "master", "discover", "reveal",
        "warning", "never", "always", "instantly", "guaranteed", "new", "now",
        "today", "essential", "powerful", "fast", "quick", "perfect", "critical",
    },
    "tr": {
        "ücretsiz", "gizli", "kanıtlanmış", "kolay", "basit", "tam", "ipuçları",
        "hata", "hatalar", "kaçının", "geliştirin", "keşfedin", "dikkat",
        "önemli", "yeni", "bugün", "hemen", "garantili", "hızlı", "kritik",
        "güçlü", "pratik", "mükemmel", "sır",
    },
    "es": {
        "gratis", "secreto", "definitivo", "probado", "mejor", "fácil",
        "simple", "guía", "trucos", "errores", "evitar", "mejorar",
        "descubrir", "atención", "importante", "nuevo", "hoy", "esencial",
    },
    "fr": {
        "gratuit", "secret", "ultime", "prouvé", "meilleur", "facile",
        "simple", "guide", "astuces", "erreurs", "éviter", "améliorer",
        "découvrir", "attention", "important", "nouveau", "essentiel",
    },
    "de": {
        "kostenlos", "geheim", "ultimativ", "bewährt", "beste", "einfach",
        "vollständig", "leitfaden", "tipps", "fehler", "vermeiden",
        "verbessern", "entdecken", "wichtig", "neu", "heute", "schnell",
    },
    "it": {
        "gratuito", "segreto", "definitivo", "provato", "migliore", "facile",
        "semplice", "guida", "trucchi", "errori", "evitare", "migliorare",
        "scoprire", "importante", "nuovo", "oggi", "essenziale",
    },
    "pt": {
        "gratuito", "segredo", "definitivo", "comprovado", "melhor", "fácil",
        "simples", "guia", "dicas", "erros", "evitar", "melhorar",
        "descobrir", "importante", "novo", "hoje", "essencial",
    },
}

_NUMBER_RE = re.compile(r"\b\d+\b")
_QUESTION_RE = re.compile(r"\?$")


async def score_title_clickability(
    titles: list[str],
    keyword: str | None = None,
    language: str = "en",
) -> TitleClickabilityReport:
    """Score a list of title candidates for estimated click-through rate.

    Applies rule-based heuristics: power words, number presence, question
    format, SERP length safety, keyword presence, and character count. No
    external calls. Useful after `suggest_titles` to pick the highest-CTR
    candidate.

    Args:
        titles: List of title strings to score (1-20).
        keyword: Target keyword; if provided, keyword-presence check runs.
        language: ISO 639-1 code for language-specific power word lists.

    Returns:
        TitleClickabilityReport with per-title scores and a top pick.
    """
    if not titles:
        raise ValueError("`titles` must be a non-empty list.")

    power_words = _POWER_WORDS.get(language, _POWER_WORDS["en"])
    items: list[TitleClickabilityItem] = []

    for title in titles[:20]:
        score, signals, missing = _score_title(title, keyword, power_words)
        items.append(
            TitleClickabilityItem(
                title=title,
                score=score,
                serp_safe=len(title) <= _SERP_SAFE_LIMIT,
                signals=signals,
                missing=missing,
            )
        )

    items.sort(key=lambda x: -x.score)
    top_pick = items[0].title if items else (titles[0] if titles else "")
    logger.info(
        "score_title_clickability titles=%d top=%r score=%d",
        len(titles),
        top_pick,
        items[0].score if items else 0,
    )
    return TitleClickabilityReport(
        keyword=keyword,
        language=language,
        items=items,
        top_pick=top_pick,
    )


def _score_title(
    title: str,
    keyword: str | None,
    power_words: set[str],
) -> tuple[int, list[str], list[str]]:
    signals: list[str] = []
    missing: list[str] = []
    score = 30  # base

    lower = title.lower()
    length = len(title)

    # Number presence (+15)
    if _NUMBER_RE.search(title):
        score += 15
        signals.append("contains number")
    else:
        missing.append("add a number (e.g. '7 Ways…', '2025')")

    # Power words (up to +25, capped at 5 words × 5 pts)
    hits = [w for w in power_words if w in lower]
    pw_score = min(len(hits) * 5, 25)
    if hits:
        score += pw_score
        signals.append(f"power word{'s' if len(hits) > 1 else ''}: {', '.join(hits[:3])}")
    else:
        missing.append("include a power word (e.g. 'best', 'guide', 'tips')")

    # SERP safety: ≤60 chars (+15)
    if length <= _SERP_SAFE_LIMIT:
        score += 15
        signals.append("SERP-safe length")
    else:
        missing.append(f"shorten to ≤{_SERP_SAFE_LIMIT} chars (currently {length})")

    # Optimal length band 40-60 (+10)
    if _OPTIMAL_MIN <= length <= _OPTIMAL_MAX:
        score += 10
        signals.append("optimal length (40-60 chars)")
    elif length < _OPTIMAL_MIN:
        missing.append("lengthen to 40+ chars for more context")

    # Question format (+10)
    if _QUESTION_RE.search(title.strip()):
        score += 10
        signals.append("question format (curiosity gap)")
    else:
        missing.append("consider a question format for curiosity gap")

    # Keyword presence (+10)
    if keyword and keyword.lower() in lower:
        score += 10
        signals.append("keyword present")
    elif keyword:
        missing.append(f"include target keyword '{keyword}'")

    return min(score, 100), signals, missing
