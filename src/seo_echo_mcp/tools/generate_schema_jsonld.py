"""generate_schema_jsonld: produce Article/BlogPosting/HowTo/Review JSON-LD."""

from __future__ import annotations

import json
from typing import Literal

from seo_echo_mcp.schemas import SchemaJsonLd

SchemaType = Literal["Article", "BlogPosting", "HowTo", "Review"]


async def generate_schema_jsonld(
    schema_type: SchemaType,
    title: str,
    description: str,
    url: str,
    author_name: str,
    published_at: str,
    image_url: str | None = None,
    keywords: list[str] | None = None,
    language: str = "en",
) -> SchemaJsonLd:
    """Build a JSON-LD block suitable for Google structured data.

    Args:
        schema_type: Article | BlogPosting | HowTo | Review.
        title, description, url: Core page metadata.
        author_name: Display name for `author.name`.
        published_at: ISO 8601 date or datetime.
        image_url: Optional hero image URL (strongly recommended by Google).
        keywords: Optional list; joined with ", " for the `keywords` field.
        language: ISO 639-1 code for `inLanguage`.

    Returns:
        SchemaJsonLd with the JSON string and a ready-to-paste <script> snippet.
    """
    data = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "headline": title,
        "description": description,
        "url": url,
        "inLanguage": language,
        "datePublished": published_at,
        "author": {"@type": "Person", "name": author_name},
    }
    if image_url:
        data["image"] = image_url
    if keywords:
        data["keywords"] = ", ".join(keywords)
    if schema_type == "HowTo":
        data["step"] = [
            {
                "@type": "HowToStep",
                "position": 1,
                "name": "<!-- WRITE: step name -->",
                "text": "<!-- WRITE: step body -->",
            }
        ]
    elif schema_type == "Review":
        data["reviewRating"] = {
            "@type": "Rating",
            "ratingValue": "<!-- FILL -->",
            "bestRating": "5",
        }
        data["itemReviewed"] = {"@type": "Thing", "name": "<!-- FILL -->"}

    json_ld = json.dumps(data, indent=2, ensure_ascii=False)
    html_snippet = f'<script type="application/ld+json">\n{json_ld}\n</script>'
    return SchemaJsonLd(schema_type=schema_type, json_ld=json_ld, html_snippet=html_snippet)
