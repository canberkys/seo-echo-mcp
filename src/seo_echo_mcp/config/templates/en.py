"""English outline templates."""

from __future__ import annotations

TITLE_TEMPLATES: list[str] = [
    "{Keyword}: A Complete Guide for {Year}",
    "How to Use {Keyword} Effectively",
    "The Best {Keyword} Strategies That Actually Work",
    "{Keyword} Explained: Everything You Need to Know",
    "Top {N} {Keyword} Techniques for {Year}",
]

META_TEMPLATES: list[str] = [
    "Looking for {keyword}? Our {year} guide walks through the essentials, best practices and real examples — read it now.",
    "Understand {keyword} in plain language. Concrete steps, common pitfalls and the patterns that actually move results.",
    "A practical {keyword} playbook: what to do first, what to measure, and how to avoid the mistakes everyone makes.",
]

H2_TEMPLATES: dict[str, list[str]] = {
    "question": ["What is {Keyword}?", "Why does {Keyword} matter?", "How does {Keyword} work?"],
    "statement": [
        "Understanding {Keyword}",
        "{Keyword} fundamentals",
        "Key principles of {Keyword}",
    ],
    "imperative": [
        "Master {Keyword} basics",
        "Apply {Keyword} to your workflow",
        "Measure your {Keyword} results",
    ],
}

CTA = "Try it in your own workflow this week and share what you learn."

META_ANGLES: dict[str, str] = {
    "problem-solution": "Struggling with {keyword}? Here's how to fix it — practical steps, common pitfalls and the approach that actually works.",
    "question": "What is {keyword} and why does it matter in {year}? A clear explanation with examples and hands-on advice.",
    "benefit": "Master {keyword} faster: real examples, proven patterns and the shortcuts experienced teams use every day.",
    "curiosity": "Everyone talks about {keyword} — but most get it wrong. Here's what actually moves results in {year}.",
    "action": "Start using {keyword} today: step-by-step instructions, templates and the metrics you should watch from day one.",
}

FAQ_QUESTION_TEMPLATES: list[str] = [
    "What is {keyword}?",
    "How does {keyword} work?",
    "Why is {keyword} important?",
    "How do I get started with {keyword}?",
    "What are common mistakes with {keyword}?",
    "How is {keyword} different from alternatives?",
]

TITLE_VARIANT_TEMPLATES: dict[str, list[str]] = {
    "listicle": [
        "{N} {Keyword} Tips You Can Use Today",
        "Top {N} {Keyword} Strategies for {Year}",
        "{N} Ways to Improve Your {Keyword}",
    ],
    "question": [
        "What Is {Keyword}? A Clear Explanation",
        "How Does {Keyword} Really Work?",
        "Why Does {Keyword} Matter in {Year}?",
    ],
    "how-to": [
        "How to Use {Keyword}: Step-by-Step Guide",
        "How to Get Started With {Keyword} in {Year}",
        "How to Master {Keyword} Without the Fluff",
    ],
    "comparison": [
        "{Keyword} vs Alternatives: Which One Wins?",
        "{Keyword} vs the Old Way: A Fair Comparison",
    ],
    "year": ["{Keyword}: The {Year} Playbook", "The State of {Keyword} in {Year}"],
    "benefit": [
        "The Benefits of {Keyword} — Explained Simply",
        "What {Keyword} Can Actually Do for You",
    ],
    "curiosity": [
        "The {Keyword} Mistake Most Teams Make",
        "What Nobody Tells You About {Keyword}",
    ],
    "statement": ["{Keyword}, Demystified", "{Keyword}: The Honest Guide"],
}

SYNTHETIC_H2_VARIANTS: list[str] = [
    "{Keyword} in practice",
    "Real-world {Keyword} scenarios",
    "{Keyword} patterns to know",
    "Common {Keyword} pitfalls",
    "{Keyword} tips and tricks",
    "Advanced {Keyword} techniques",
    "{Keyword} best practices",
    "Troubleshooting {Keyword} issues",
    "{Keyword} in production",
    "Optimizing {Keyword} performance",
    "{Keyword} use cases",
    "Comparing {Keyword} approaches",
]

MUST_COVER_INTRO: list[str] = [
    "Define {keyword}",
    "Why it matters right now",
    "Who this article is for",
]
MUST_COVER_CORE: list[str] = [
    "Core concept around {keyword}",
    "Practical application",
    "Example or case",
]
MUST_COVER_TOPIC: list[str] = [
    "Explain the role of {topic} in {keyword}",
    "Concrete examples",
    "Common pitfalls",
]
MUST_COVER_SUMMARY: list[str] = [
    "Key takeaways",
    "Next action for the reader",
]

IMAGE_ALT_TEMPLATES: dict[str, str] = {
    "filename": "{stem}",
    "keyword_with_stem": "{keyword} — {stem}",
    "keyword_with_topic": "{keyword}: {topic}",
    "topic_only": "{topic}",
}

# Style-specific wrapper applied to a base H2 (synthetic or topic-joined).
H2_STYLE_TEMPLATES: dict[str, str] = {
    "question": "What is {base}?",
    "imperative": "Master {base}",
    "statement": "{base}",
    "mixed": "{base}",
}

# Summary section H2 per style (last section of an outline).
SUMMARY_H2: dict[str, str] = {
    "question": "What should you do next with {keyword}?",
    "imperative": "Put {keyword} into practice",
    "statement": "{keyword}: key takeaways",
    "mixed": "{keyword}: key takeaways",
}

# Connector when an H2 joins the keyword to a competitor topic ("X and Y").
TOPIC_CONNECTOR = "and"
