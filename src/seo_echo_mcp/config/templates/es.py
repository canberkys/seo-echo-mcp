"""Spanish outline templates."""

from __future__ import annotations

TITLE_TEMPLATES: list[str] = [
    "{Keyword}: Guía Completa para {Year}",
    "Cómo Usar {Keyword} de Forma Efectiva",
    "Las Mejores Estrategias de {Keyword} que Realmente Funcionan",
    "{Keyword} Explicado: Todo lo que Necesitas Saber",
    "{N} Técnicas de {Keyword} para {Year}",
]

META_TEMPLATES: list[str] = [
    "¿Buscas {keyword}? Nuestra guía de {year} cubre lo esencial, las mejores prácticas y ejemplos reales.",
    "Entiende {keyword} con un lenguaje sencillo: pasos concretos, errores comunes y los patrones que funcionan.",
    "Un manual práctico de {keyword}: qué hacer primero, qué medir y cómo evitar los errores habituales.",
]

H2_TEMPLATES: dict[str, list[str]] = {
    "question": ["¿Qué es {Keyword}?", "¿Por qué importa {Keyword}?", "¿Cómo funciona {Keyword}?"],
    "statement": [
        "Fundamentos de {Keyword}",
        "Entendiendo {Keyword}",
        "Principios clave de {Keyword}",
    ],
    "imperative": [
        "Domina los básicos de {Keyword}",
        "Aplica {Keyword} a tu flujo de trabajo",
        "Mide tus resultados de {Keyword}",
    ],
}

CTA = "Pruébalo en tu flujo esta semana y comparte lo que aprendas."

META_ANGLES: dict[str, str] = {
    "problem-solution": "¿Tienes problemas con {keyword}? Aquí la solución: pasos prácticos, errores comunes y el enfoque que realmente funciona.",
    "question": "¿Qué es {keyword} y por qué importa en {year}? Explicación clara, ejemplos concretos y consejos aplicables.",
    "benefit": "Domina {keyword} más rápido: ejemplos reales, patrones probados y atajos que usan los equipos experimentados.",
    "curiosity": "Todo el mundo habla de {keyword} — pero la mayoría se equivoca. Esto es lo que funciona en {year}.",
    "action": "Empieza a usar {keyword} hoy: instrucciones paso a paso, plantillas y las métricas a vigilar desde el primer día.",
}

FAQ_QUESTION_TEMPLATES: list[str] = [
    "¿Qué es {keyword}?",
    "¿Cómo funciona {keyword}?",
    "¿Por qué es importante {keyword}?",
    "¿Cómo empiezo con {keyword}?",
    "¿Cuáles son los errores comunes con {keyword}?",
    "¿En qué se diferencia {keyword} de sus alternativas?",
]

TITLE_VARIANT_TEMPLATES: dict[str, list[str]] = {
    "listicle": [
        "{N} Consejos de {Keyword} que Puedes Usar Hoy",
        "Top {N} Estrategias de {Keyword} para {Year}",
        "{N} Formas de Mejorar tu {Keyword}",
    ],
    "question": [
        "¿Qué es {Keyword}? Una Explicación Clara",
        "¿Cómo Funciona Realmente {Keyword}?",
        "¿Por Qué Importa {Keyword} en {Year}?",
    ],
    "how-to": [
        "Cómo Usar {Keyword}: Guía Paso a Paso",
        "Cómo Empezar con {Keyword} en {Year}",
        "Cómo Dominar {Keyword} sin Vueltas",
    ],
    "comparison": [
        "{Keyword} vs Alternativas: ¿Cuál Gana?",
        "{Keyword} vs el Método Antiguo: Comparación Justa",
    ],
    "year": ["{Keyword}: El Manual para {Year}", "El Estado de {Keyword} en {Year}"],
    "benefit": [
        "Los Beneficios de {Keyword} — Explicados Claramente",
        "Lo que {Keyword} Puede Hacer por Ti",
    ],
    "curiosity": [
        "El Error de {Keyword} que Cometen Casi Todos los Equipos",
        "Lo que Nadie te Cuenta sobre {Keyword}",
    ],
    "statement": ["{Keyword}, Desmitificado", "{Keyword}: La Guía Honesta"],
}

SYNTHETIC_H2_VARIANTS: list[str] = [
    "{Keyword} en la práctica",
    "Escenarios reales de {Keyword}",
    "Patrones de {Keyword} que debes conocer",
    "Errores comunes con {Keyword}",
    "Consejos y trucos de {Keyword}",
    "Técnicas avanzadas de {Keyword}",
    "Mejores prácticas para {Keyword}",
    "Resolución de problemas con {Keyword}",
    "{Keyword} en producción",
    "Optimizando el rendimiento de {Keyword}",
    "Casos de uso de {Keyword}",
    "Comparando enfoques de {Keyword}",
]

MUST_COVER_INTRO: list[str] = [
    "Define {keyword}",
    "Por qué importa ahora",
    "Para quién es este artículo",
]
MUST_COVER_CORE: list[str] = [
    "Concepto clave de {keyword}",
    "Aplicación práctica",
    "Ejemplo o caso",
]
MUST_COVER_TOPIC: list[str] = [
    "Explica el papel de {topic} en {keyword}",
    "Ejemplos concretos",
    "Errores habituales",
]
MUST_COVER_SUMMARY: list[str] = [
    "Conclusiones clave",
    "Próxima acción para el lector",
]

IMAGE_ALT_TEMPLATES: dict[str, str] = {
    "filename": "{stem}",
    "keyword_with_stem": "{keyword} — {stem}",
    "keyword_with_topic": "{keyword}: {topic}",
    "topic_only": "{topic}",
}

H2_STYLE_TEMPLATES: dict[str, str] = {
    "question": "¿Qué es {base}?",
    "imperative": "Domina {base}",
    "statement": "{base}",
    "mixed": "{base}",
}

SUMMARY_H2: dict[str, str] = {
    "question": "¿Qué deberías hacer a continuación con {keyword}?",
    "imperative": "Pon {keyword} en práctica",
    "statement": "{keyword}: conclusiones clave",
    "mixed": "{keyword}: conclusiones clave",
}

TOPIC_CONNECTOR = "y"
