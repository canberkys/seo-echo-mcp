"""French outline templates."""

from __future__ import annotations

TITLE_TEMPLATES: list[str] = [
    "{Keyword} : Le Guide Complet pour {Year}",
    "Comment Utiliser {Keyword} Efficacement",
    "Les Meilleures Stratégies {Keyword} qui Fonctionnent Vraiment",
    "{Keyword} Expliqué : Tout ce que Vous Devez Savoir",
    "{N} Techniques {Keyword} pour {Year}",
]

META_TEMPLATES: list[str] = [
    "À la recherche de {keyword} ? Notre guide {year} couvre l'essentiel, les bonnes pratiques et des exemples réels.",
    "Comprenez {keyword} simplement : étapes concrètes, pièges fréquents et méthodes qui marchent vraiment.",
    "Un manuel pratique {keyword} : par où commencer, quoi mesurer et comment éviter les erreurs courantes.",
]

H2_TEMPLATES: dict[str, list[str]] = {
    "question": [
        "Qu'est-ce que {Keyword} ?",
        "Pourquoi {Keyword} est-il important ?",
        "Comment fonctionne {Keyword} ?",
    ],
    "statement": [
        "Les fondamentaux de {Keyword}",
        "Comprendre {Keyword}",
        "Les principes clés de {Keyword}",
    ],
    "imperative": [
        "Maîtrisez les bases de {Keyword}",
        "Appliquez {Keyword} à votre flux",
        "Mesurez vos résultats {Keyword}",
    ],
}

CTA = "Essayez-le dans votre flux cette semaine et partagez vos retours."

META_ANGLES: dict[str, str] = {
    "problem-solution": "Bloqué sur {keyword} ? Voici comment s'en sortir : étapes concrètes, pièges fréquents et l'approche qui fonctionne vraiment.",
    "question": "Qu'est-ce que {keyword} et pourquoi est-ce important en {year} ? Explication claire avec exemples et conseils pratiques.",
    "benefit": "Maîtrisez {keyword} plus vite : exemples réels, modèles éprouvés et raccourcis utilisés par les équipes expérimentées.",
    "curiosity": "Tout le monde parle de {keyword} — mais la plupart se trompent. Voici ce qui fonctionne vraiment en {year}.",
    "action": "Commencez à utiliser {keyword} dès aujourd'hui : instructions pas à pas, modèles et les métriques à surveiller.",
}

FAQ_QUESTION_TEMPLATES: list[str] = [
    "Qu'est-ce que {keyword} ?",
    "Comment fonctionne {keyword} ?",
    "Pourquoi {keyword} est-il important ?",
    "Comment commencer avec {keyword} ?",
    "Quelles sont les erreurs fréquentes avec {keyword} ?",
    "En quoi {keyword} diffère-t-il des alternatives ?",
]

TITLE_VARIANT_TEMPLATES: dict[str, list[str]] = {
    "listicle": [
        "{N} Astuces {Keyword} à Utiliser dès Aujourd'hui",
        "Top {N} Stratégies {Keyword} pour {Year}",
        "{N} Façons d'Améliorer Votre {Keyword}",
    ],
    "question": [
        "Qu'est-ce que {Keyword} ? Une Explication Claire",
        "Comment Fonctionne Vraiment {Keyword} ?",
        "Pourquoi {Keyword} Est-il Important en {Year} ?",
    ],
    "how-to": [
        "Comment Utiliser {Keyword} : Guide Étape par Étape",
        "Comment Démarrer avec {Keyword} en {Year}",
        "Comment Maîtriser {Keyword} sans Détours",
    ],
    "comparison": [
        "{Keyword} vs Alternatives : Qui Gagne ?",
        "{Keyword} vs l'Ancienne Méthode : Comparaison Honnête",
    ],
    "year": ["{Keyword} : Le Manuel {Year}", "L'État de {Keyword} en {Year}"],
    "benefit": [
        "Les Avantages de {Keyword} — Expliqués Simplement",
        "Ce que {Keyword} Peut Vraiment Faire pour Vous",
    ],
    "curiosity": [
        "L'Erreur {Keyword} que Font la Plupart des Équipes",
        "Ce que Personne ne Vous Dit sur {Keyword}",
    ],
    "statement": ["{Keyword}, Démystifié", "{Keyword} : Le Guide Honnête"],
}

SYNTHETIC_H2_VARIANTS: list[str] = [
    "{Keyword} en pratique",
    "Scénarios réels de {Keyword}",
    "Motifs de {Keyword} à connaître",
    "Pièges courants avec {Keyword}",
    "Astuces et conseils {Keyword}",
    "Techniques avancées de {Keyword}",
    "Bonnes pratiques {Keyword}",
    "Dépannage des problèmes {Keyword}",
    "{Keyword} en production",
    "Optimiser les performances de {Keyword}",
    "Cas d'usage de {Keyword}",
    "Comparer les approches {Keyword}",
]

MUST_COVER_INTRO: list[str] = [
    "Définir {keyword}",
    "Pourquoi cela compte maintenant",
    "À qui s'adresse cet article",
]
MUST_COVER_CORE: list[str] = [
    "Concept clé autour de {keyword}",
    "Application pratique",
    "Exemple ou cas",
]
MUST_COVER_TOPIC: list[str] = [
    "Expliquer le rôle de {topic} dans {keyword}",
    "Exemples concrets",
    "Pièges habituels",
]
MUST_COVER_SUMMARY: list[str] = [
    "Points clés à retenir",
    "Prochaine action pour le lecteur",
]

IMAGE_ALT_TEMPLATES: dict[str, str] = {
    "filename": "{stem}",
    "keyword_with_stem": "{keyword} — {stem}",
    "keyword_with_topic": "{keyword} : {topic}",
    "topic_only": "{topic}",
}

H2_STYLE_TEMPLATES: dict[str, str] = {
    "question": "Qu'est-ce que {base} ?",
    "imperative": "Maîtrisez {base}",
    "statement": "{base}",
    "mixed": "{base}",
}

SUMMARY_H2: dict[str, str] = {
    "question": "Que faire ensuite avec {keyword} ?",
    "imperative": "Mettez {keyword} en pratique",
    "statement": "{keyword} : points clés",
    "mixed": "{keyword} : points clés",
}

TOPIC_CONNECTOR = "et"
