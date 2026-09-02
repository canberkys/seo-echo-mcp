"""Italian outline templates."""

from __future__ import annotations

TITLE_TEMPLATES: list[str] = [
    "{Keyword}: Guida Completa per il {Year}",
    "Come Usare {Keyword} in Modo Efficace",
    "Le Migliori Strategie di {Keyword} che Funzionano Davvero",
    "{Keyword} Spiegato: Tutto Quello che Devi Sapere",
    "Top {N} Tecniche di {Keyword} per il {Year}",
]

META_TEMPLATES: list[str] = [
    "Cerchi informazioni su {keyword}? La nostra guida {year} illustra le basi, le migliori pratiche ed esempi concreti — leggi subito.",
    "Scopri {keyword} in modo chiaro. Passi pratici, errori comuni e i pattern che portano risultati reali.",
    "Il manuale pratico su {keyword}: cosa fare prima, cosa misurare e come evitare gli errori più comuni.",
]

H2_TEMPLATES: dict[str, list[str]] = {
    "question": [
        "Che cos'è {Keyword}?",
        "Perché {Keyword} è importante?",
        "Come funziona {Keyword}?",
    ],
    "statement": [
        "Capire {Keyword}",
        "Fondamenti di {Keyword}",
        "Principi chiave di {Keyword}",
    ],
    "imperative": [
        "Padroneggia le basi di {Keyword}",
        "Applica {Keyword} al tuo lavoro",
        "Misura i risultati con {Keyword}",
    ],
}

CTA = "Prova nella tua routine questa settimana e condividi quello che hai imparato."

META_ANGLES: dict[str, str] = {
    "problem-solution": "Hai difficoltà con {keyword}? Ecco come risolverlo — passi pratici, errori frequenti e l'approccio che funziona davvero.",
    "question": "Cos'è {keyword} e perché conta nel {year}? Una spiegazione chiara con esempi e consigli pratici.",
    "benefit": "Padroneggia {keyword} più velocemente: esempi reali, pattern consolidati e le scorciatoie che i team esperti usano ogni giorno.",
    "curiosity": "Tutti parlano di {keyword} — ma la maggior parte sbaglia approccio. Ecco cosa porta risultati reali nel {year}.",
    "action": "Inizia a usare {keyword} oggi: istruzioni passo dopo passo, template e le metriche da monitorare dal primo giorno.",
}

FAQ_QUESTION_TEMPLATES: list[str] = [
    "Che cos'è {keyword}?",
    "Come funziona {keyword}?",
    "Perché {keyword} è importante?",
    "Come posso iniziare con {keyword}?",
    "Quali sono gli errori più comuni con {keyword}?",
    "In che cosa {keyword} si distingue dalle alternative?",
]

TITLE_VARIANT_TEMPLATES: dict[str, list[str]] = {
    "listicle": [
        "{N} Consigli su {Keyword} da Usare Subito",
        "I Migliori {N} Approcci a {Keyword} per il {Year}",
        "{N} Modi per Migliorare il tuo {Keyword}",
    ],
    "question": [
        "Cos'è {Keyword}? Una Spiegazione Chiara",
        "Come Funziona Davvero {Keyword}?",
        "Perché {Keyword} Conta nel {Year}?",
    ],
    "how-to": [
        "Come Usare {Keyword}: Guida Passo dopo Passo",
        "Come Iniziare con {Keyword} nel {Year}",
        "Come Padroneggiare {Keyword} Senza Sprechi di Tempo",
    ],
    "comparison": [
        "{Keyword} vs Alternative: Chi Vince?",
        "{Keyword} vs il Vecchio Metodo: Un Confronto Equo",
    ],
    "year": ["{Keyword}: Il Manuale del {Year}", "Lo Stato di {Keyword} nel {Year}"],
    "benefit": [
        "I Vantaggi di {Keyword} — Spiegati Semplicemente",
        "Cosa Può Fare {Keyword} per Te",
    ],
    "curiosity": [
        "L'Errore di {Keyword} che la Maggior Parte Commette",
        "Quello che Nessuno Ti Dice su {Keyword}",
    ],
    "statement": ["{Keyword}, Demistificato", "{Keyword}: La Guida Onesta"],
}

SYNTHETIC_H2_VARIANTS: list[str] = [
    "{Keyword} nella pratica",
    "Scenari reali con {Keyword}",
    "Pattern di {Keyword} da conoscere",
    "Errori comuni con {Keyword}",
    "Suggerimenti e trucchi su {Keyword}",
    "Tecniche avanzate di {Keyword}",
    "Best practice per {Keyword}",
    "Risolvere i problemi con {Keyword}",
    "{Keyword} in produzione",
    "Ottimizzare le performance di {Keyword}",
    "Casi d'uso di {Keyword}",
    "Confronto tra approcci a {Keyword}",
]

MUST_COVER_INTRO: list[str] = [
    "Definire {keyword}",
    "Perché conta in questo momento",
    "A chi si rivolge questo articolo",
]
MUST_COVER_CORE: list[str] = [
    "Concetto centrale di {keyword}",
    "Applicazione pratica",
    "Esempio o caso studio",
]
MUST_COVER_TOPIC: list[str] = [
    "Spiegare il ruolo di {topic} in {keyword}",
    "Esempi concreti",
    "Errori frequenti",
]
MUST_COVER_SUMMARY: list[str] = [
    "Punti chiave",
    "Prossimo passo per il lettore",
]

IMAGE_ALT_TEMPLATES: dict[str, str] = {
    "filename": "{stem}",
    "keyword_with_stem": "{keyword} — {stem}",
    "keyword_with_topic": "{keyword}: {topic}",
    "topic_only": "{topic}",
}

H2_STYLE_TEMPLATES: dict[str, str] = {
    "question": "Cos'è {base}?",
    "imperative": "Padroneggia {base}",
    "statement": "{base}",
    "mixed": "{base}",
}

SUMMARY_H2: dict[str, str] = {
    "question": "Qual è il prossimo passo con {keyword}?",
    "imperative": "Metti in pratica {keyword}",
    "statement": "{keyword}: punti chiave",
    "mixed": "{keyword}: punti chiave",
}

TOPIC_CONNECTOR = "e"
