"""generate_faq_section: build a FAQ block + FAQPage JSON-LD for a keyword."""

from __future__ import annotations

import json
import re

from seo_echo_mcp.config.templates.loader import load as load_templates
from seo_echo_mcp.schemas import CompetitorAnalysis, FaqItem, FaqSection


async def generate_faq_section(
    keyword: str,
    language: str = "en",
    competitor_analysis: CompetitorAnalysis | None = None,
    count: int = 5,
) -> FaqSection:
    """Produce an FAQ section with 5 questions and FAQPage structured data.

    Question selection:
      1. Language-specific FAQ templates (`config/templates/<lang>.FAQ_QUESTION_TEMPLATES`).
      2. If competitor_analysis is given, question-shaped H2s (ending with ?)
         from the top results are mixed in — these mirror real PAA intent.

    Answers are NOT generated here — each answer slot is a `<!-- WRITE: ... -->`
    directive the host LLM fills while drafting.

    Args:
        keyword: Target keyword (substituted into question templates).
        language: ISO 639-1 code.
        competitor_analysis: Optional CompetitorAnalysis; question-shaped H2s
            are harvested from its results.
        count: Number of FAQ items (default 5).

    Returns:
        FaqSection with items, a ready-to-embed markdown block, and a
        FAQPage JSON-LD string.
    """
    tpl = load_templates(language)
    questions = _collect_questions(keyword, tpl, competitor_analysis, count)
    items = [
        FaqItem(
            position=i + 1,
            question=q,
            answer_directive=f"<!-- WRITE: 50-80 words. Language: {language}. Answer directly, cite concrete example. -->",
        )
        for i, q in enumerate(questions)
    ]
    markdown = _render_markdown(items, language)
    jsonld = _render_jsonld(items, language)
    return FaqSection(
        keyword=keyword, language=language, items=items, markdown=markdown, faq_jsonld=jsonld
    )


def _collect_questions(
    keyword: str,
    tpl,
    comp: CompetitorAnalysis | None,
    count: int,
) -> list[str]:
    pool: list[str] = []
    for t in tpl.FAQ_QUESTION_TEMPLATES:
        pool.append(t.format(keyword=keyword))
    if comp:
        for entry in comp.results:
            for h2 in entry.h2s:
                if h2.rstrip().endswith("?") and h2 not in pool:
                    pool.append(h2)
    # Deduplicate preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for q in pool:
        key = re.sub(r"\s+", " ", q.strip().lower())
        if key not in seen:
            seen.add(key)
            unique.append(q.strip())
    return unique[:count]


def _render_markdown(items: list[FaqItem], language: str) -> str:
    heading = _faq_heading(language)
    lines = [f"## {heading}", ""]
    for item in items:
        lines.append(f"### {item.question}")
        lines.append("")
        lines.append(item.answer_directive)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _faq_heading(language: str) -> str:
    return {
        "en": "Frequently Asked Questions",
        "tr": "Sıkça Sorulan Sorular",
        "es": "Preguntas Frecuentes",
        "fr": "Questions Fréquentes",
        "de": "Häufig gestellte Fragen",
    }.get(language, "Frequently Asked Questions")


def _render_jsonld(items: list[FaqItem], language: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": language,
        "mainEntity": [
            {
                "@type": "Question",
                "name": item.question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "<!-- WRITE answer here before publishing -->",
                },
            }
            for item in items
        ],
    }
    return json.dumps(data, indent=2, ensure_ascii=False)
