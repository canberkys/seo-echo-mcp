"""German outline templates."""

from __future__ import annotations

TITLE_TEMPLATES: list[str] = [
    "{Keyword}: Der vollständige Leitfaden für {Year}",
    "Wie Sie {Keyword} effektiv nutzen",
    "Die besten {Keyword}-Strategien, die wirklich funktionieren",
    "{Keyword} erklärt: Alles, was Sie wissen müssen",
    "{N} {Keyword}-Techniken für {Year}",
]

META_TEMPLATES: list[str] = [
    "Suchen Sie {keyword}? Unser {year}-Leitfaden zeigt Grundlagen, Best Practices und echte Beispiele.",
    "Verstehen Sie {keyword} in klarer Sprache: konkrete Schritte, häufige Fehler und Muster, die wirken.",
    "Ein praktisches {keyword}-Handbuch: womit anfangen, was messen und wie typische Fehler vermeiden.",
]

H2_TEMPLATES: dict[str, list[str]] = {
    "question": [
        "Was ist {Keyword}?",
        "Warum ist {Keyword} wichtig?",
        "Wie funktioniert {Keyword}?",
    ],
    "statement": [
        "{Keyword}-Grundlagen",
        "{Keyword} verstehen",
        "Schlüsselprinzipien von {Keyword}",
    ],
    "imperative": [
        "Beherrschen Sie die {Keyword}-Basics",
        "Wenden Sie {Keyword} in Ihrem Workflow an",
        "Messen Sie Ihre {Keyword}-Ergebnisse",
    ],
}

CTA = "Testen Sie es diese Woche in Ihrem Workflow und teilen Sie Ihre Erkenntnisse."

META_ANGLES: dict[str, str] = {
    "problem-solution": "Sie kommen bei {keyword} nicht weiter? So lösen Sie es: praktische Schritte, typische Fehler und der Ansatz, der wirklich funktioniert.",
    "question": "Was ist {keyword} und warum ist es {year} wichtig? Klare Erklärung mit Beispielen und umsetzbaren Tipps.",
    "benefit": "Meistern Sie {keyword} schneller: echte Beispiele, bewährte Muster und die Abkürzungen erfahrener Teams.",
    "curiosity": "Alle reden über {keyword} — aber die meisten machen es falsch. Das funktioniert wirklich in {year}.",
    "action": "Starten Sie heute mit {keyword}: Schritt-für-Schritt-Anleitung, Vorlagen und die Metriken, die Sie ab Tag eins verfolgen sollten.",
}

FAQ_QUESTION_TEMPLATES: list[str] = [
    "Was ist {keyword}?",
    "Wie funktioniert {keyword}?",
    "Warum ist {keyword} wichtig?",
    "Wie fange ich mit {keyword} an?",
    "Welche typischen Fehler gibt es bei {keyword}?",
    "Wie unterscheidet sich {keyword} von Alternativen?",
]

TITLE_VARIANT_TEMPLATES: dict[str, list[str]] = {
    "listicle": [
        "{N} {Keyword}-Tipps für den sofortigen Einsatz",
        "Top {N} {Keyword}-Strategien für {Year}",
        "{N} Wege, Ihr {Keyword} zu verbessern",
    ],
    "question": [
        "Was ist {Keyword}? Eine klare Erklärung",
        "Wie funktioniert {Keyword} wirklich?",
        "Warum ist {Keyword} in {Year} wichtig?",
    ],
    "how-to": [
        "So verwenden Sie {Keyword}: Schritt-für-Schritt-Anleitung",
        "So starten Sie mit {Keyword} in {Year}",
        "So meistern Sie {Keyword} ohne Umwege",
    ],
    "comparison": [
        "{Keyword} vs Alternativen: Welche Lösung gewinnt?",
        "{Keyword} vs der alte Weg: Ein fairer Vergleich",
    ],
    "year": ["{Keyword}: Das {Year}-Playbook", "Der Stand von {Keyword} in {Year}"],
    "benefit": [
        "Die Vorteile von {Keyword} — einfach erklärt",
        "Was {Keyword} wirklich für Sie tun kann",
    ],
    "curiosity": [
        "Der {Keyword}-Fehler, den die meisten Teams machen",
        "Was Ihnen niemand über {Keyword} sagt",
    ],
    "statement": ["{Keyword}, entmystifiziert", "{Keyword}: Der ehrliche Leitfaden"],
}
