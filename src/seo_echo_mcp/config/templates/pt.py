"""Portuguese outline templates."""

from __future__ import annotations

TITLE_TEMPLATES: list[str] = [
    "{Keyword}: Guia Completo para {Year}",
    "Como Usar {Keyword} de Forma Eficaz",
    "As Melhores Estratégias de {Keyword} que Realmente Funcionam",
    "{Keyword} Explicado: Tudo o que Você Precisa Saber",
    "Top {N} Técnicas de {Keyword} para {Year}",
]

META_TEMPLATES: list[str] = [
    "Procurando informações sobre {keyword}? Nosso guia {year} explica as bases, as melhores práticas e exemplos concretos — leia agora.",
    "Descubra {keyword} de forma clara. Passos práticos, erros comuns e os padrões que trazem resultados reais.",
    "O manual prático sobre {keyword}: o que fazer primeiro, o que medir e como evitar os erros mais comuns.",
]

H2_TEMPLATES: dict[str, list[str]] = {
    "question": [
        "O que é {Keyword}?",
        "Por que {Keyword} é importante?",
        "Como funciona {Keyword}?",
    ],
    "statement": [
        "Entendendo {Keyword}",
        "Fundamentos de {Keyword}",
        "Princípios-chave de {Keyword}",
    ],
    "imperative": [
        "Domine os fundamentos de {Keyword}",
        "Aplique {Keyword} no seu trabalho",
        "Meça os resultados com {Keyword}",
    ],
}

CTA = "Experimente na sua rotina esta semana e compartilhe o que você aprendeu."

META_ANGLES: dict[str, str] = {
    "problem-solution": "Tem dificuldades com {keyword}? Veja como resolver — passos práticos, erros frequentes e a abordagem que realmente funciona.",
    "question": "O que é {keyword} e por que importa em {year}? Uma explicação clara com exemplos e dicas práticas.",
    "benefit": "Domine {keyword} mais rápido: exemplos reais, padrões consolidados e os atalhos que equipes experientes usam todo dia.",
    "curiosity": "Todo mundo fala de {keyword} — mas a maioria erra a abordagem. Veja o que realmente traz resultados em {year}.",
    "action": "Comece a usar {keyword} hoje: instruções passo a passo, templates e as métricas para acompanhar desde o primeiro dia.",
}

FAQ_QUESTION_TEMPLATES: list[str] = [
    "O que é {keyword}?",
    "Como funciona {keyword}?",
    "Por que {keyword} é importante?",
    "Como posso começar com {keyword}?",
    "Quais são os erros mais comuns com {keyword}?",
    "Em que {keyword} se diferencia das alternativas?",
]

TITLE_VARIANT_TEMPLATES: dict[str, list[str]] = {
    "listicle": [
        "{N} Dicas sobre {Keyword} para Usar Agora",
        "As Melhores {N} Abordagens de {Keyword} para {Year}",
        "{N} Maneiras de Melhorar seu {Keyword}",
    ],
    "question": [
        "O que é {Keyword}? Uma Explicação Clara",
        "Como {Keyword} Realmente Funciona?",
        "Por que {Keyword} Importa em {Year}?",
    ],
    "how-to": [
        "Como Usar {Keyword}: Guia Passo a Passo",
        "Como Começar com {Keyword} em {Year}",
        "Como Dominar {Keyword} sem Perder Tempo",
    ],
    "comparison": [
        "{Keyword} vs Alternativas: Quem Ganha?",
        "{Keyword} vs o Método Antigo: Uma Comparação Justa",
    ],
    "year": ["{Keyword}: O Manual de {Year}", "O Estado de {Keyword} em {Year}"],
    "benefit": [
        "As Vantagens de {Keyword} — Explicadas de Forma Simples",
        "O que {Keyword} Pode Fazer por Você",
    ],
    "curiosity": [
        "O Erro de {Keyword} que a Maioria Comete",
        "O que Ninguém te Conta sobre {Keyword}",
    ],
    "statement": ["{Keyword}, Desmistificado", "{Keyword}: O Guia Honesto"],
}

SYNTHETIC_H2_VARIANTS: list[str] = [
    "{Keyword} na prática",
    "Cenários reais com {Keyword}",
    "Padrões de {Keyword} para conhecer",
    "Erros comuns com {Keyword}",
    "Dicas e truques sobre {Keyword}",
    "Técnicas avançadas de {Keyword}",
    "Boas práticas para {Keyword}",
    "Resolvendo problemas com {Keyword}",
    "{Keyword} em produção",
    "Otimizando a performance de {Keyword}",
    "Casos de uso de {Keyword}",
    "Comparação entre abordagens de {Keyword}",
]

MUST_COVER_INTRO: list[str] = [
    "Definir {keyword}",
    "Por que importa agora",
    "Para quem é este artigo",
]
MUST_COVER_CORE: list[str] = [
    "Conceito central de {keyword}",
    "Aplicação prática",
    "Exemplo ou estudo de caso",
]
MUST_COVER_TOPIC: list[str] = [
    "Explicar o papel de {topic} em {keyword}",
    "Exemplos concretos",
    "Erros frequentes",
]
MUST_COVER_SUMMARY: list[str] = [
    "Pontos-chave",
    "Próximo passo para o leitor",
]

IMAGE_ALT_TEMPLATES: dict[str, str] = {
    "filename": "{stem}",
    "keyword_with_stem": "{keyword} — {stem}",
    "keyword_with_topic": "{keyword}: {topic}",
    "topic_only": "{topic}",
}

H2_STYLE_TEMPLATES: dict[str, str] = {
    "question": "O que é {base}?",
    "imperative": "Domine {base}",
    "statement": "{base}",
    "mixed": "{base}",
}

SUMMARY_H2: dict[str, str] = {
    "question": "Qual é o próximo passo com {keyword}?",
    "imperative": "Coloque {keyword} em prática",
    "statement": "{keyword}: pontos-chave",
    "mixed": "{keyword}: pontos-chave",
}

TOPIC_CONNECTOR = "e"
