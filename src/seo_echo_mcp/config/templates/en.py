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
