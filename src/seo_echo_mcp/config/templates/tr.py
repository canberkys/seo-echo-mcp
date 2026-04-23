"""Turkish outline templates."""

from __future__ import annotations

TITLE_TEMPLATES: list[str] = [
    "{Keyword} Rehberi: {Year} İçin Eksiksiz Yol Haritası",
    "{Keyword} Nasıl Kullanılır? Adım Adım Açıklıyoruz",
    "En İyi {Keyword} Stratejileri: Gerçekten İşe Yarayanlar",
    "{Keyword} Nedir? {Year} İçin Bilmeniz Gerekenler",
    "{N} Maddede {Keyword}: Pratik Teknikler",
]

META_TEMPLATES: list[str] = [
    "{keyword} hakkında merak ettiğiniz her şey tek yerde. {year} için güncel ipuçları, pratik örnekler ve adım adım rehber.",
    "{keyword} konusunu sade bir dille açıklıyoruz. Somut adımlar, yaygın hatalar ve gerçekten işe yarayan yöntemler.",
    "Uygulamaya yönelik bir {keyword} rehberi: nereden başlamalı, neyi ölçmeli, hangi tuzaklardan kaçınmalısınız?",
]

H2_TEMPLATES: dict[str, list[str]] = {
    "question": ["{Keyword} nedir?", "{Keyword} neden önemlidir?", "{Keyword} nasıl çalışır?"],
    "statement": [
        "{Keyword} temelleri",
        "{Keyword} hakkında bilmeniz gerekenler",
        "{Keyword} anahtar kavramları",
    ],
    "imperative": [
        "{Keyword} temellerini öğrenin",
        "{Keyword} iş akışınıza ekleyin",
        "{Keyword} sonuçlarınızı ölçün",
    ],
}

CTA = "Bu hafta kendi iş akışında dene, sonuçları paylaş."

META_ANGLES: dict[str, str] = {
    "problem-solution": "{keyword} konusunda takılıyor musun? Sorunu çözmenin pratik adımları, sık yapılan hatalar ve gerçekten işe yarayan yaklaşım burada.",
    "question": "{keyword} nedir ve {year} yılında neden önemli? Sade bir açıklama, somut örnekler ve uygulanabilir tavsiyeler.",
    "benefit": "{keyword} konusunda hız kazan: gerçek örnekler, kanıtlanmış yöntemler ve deneyimli ekiplerin her gün kullandığı kısayollar.",
    "curiosity": "Herkes {keyword} konuşuyor — ama çoğu yanlış biliyor. {year} için gerçekten sonuç getiren yaklaşım burada.",
    "action": "Bugün {keyword} kullanmaya başla: adım adım talimatlar, şablonlar ve ilk günden takip etmen gereken metrikler.",
}

FAQ_QUESTION_TEMPLATES: list[str] = [
    "{keyword} nedir?",
    "{keyword} nasıl çalışır?",
    "{keyword} neden önemlidir?",
    "{keyword} ile nasıl başlarım?",
    "{keyword} kullanırken sık yapılan hatalar nelerdir?",
    "{keyword} alternatiflerinden nasıl ayrışır?",
]

TITLE_VARIANT_TEMPLATES: dict[str, list[str]] = {
    "listicle": [
        "{N} Maddede {Keyword} İpuçları",
        "{Year} İçin En İyi {N} {Keyword} Stratejisi",
        "{Keyword}'i Geliştirmenin {N} Yolu",
    ],
    "question": [
        "{Keyword} Nedir? Kısa ve Net Açıklama",
        "{Keyword} Nasıl Çalışır?",
        "{Keyword} {Year} İçin Neden Önemli?",
    ],
    "how-to": [
        "{Keyword} Nasıl Kullanılır: Adım Adım Rehber",
        "{Year} İçin {Keyword} ile Nasıl Başlanır",
        "Fazlalık Olmadan {Keyword} Nasıl Öğrenilir",
    ],
    "comparison": [
        "{Keyword} vs Alternatifler: Hangisi Kazanır?",
        "{Keyword} vs Eski Yöntem: Adil Bir Karşılaştırma",
    ],
    "year": ["{Keyword}: {Year} Oyun Kitabı", "{Year} İtibariyle {Keyword} Durumu"],
    "benefit": [
        "{Keyword}'in Faydaları — Sade Anlatım",
        "{Keyword} Senin İçin Gerçekten Ne Yapabilir?",
    ],
    "curiosity": [
        "Çoğu Ekibin {Keyword} Konusunda Yaptığı Hata",
        "Kimsenin Sana Söylemediği {Keyword} Gerçeği",
    ],
    "statement": ["{Keyword}, Açıkça Anlatıldı", "{Keyword}: Dürüst Rehber"],
}

SYNTHETIC_H2_VARIANTS: list[str] = [
    "{Keyword} pratikte",
    "Gerçek dünyada {Keyword} senaryoları",
    "Bilmeniz gereken {Keyword} desenleri",
    "{Keyword} yaparken sık yapılan hatalar",
    "{Keyword} ipuçları ve püf noktaları",
    "İleri düzey {Keyword} teknikleri",
    "{Keyword} için en iyi uygulamalar",
    "{Keyword} sorunlarında sorun giderme",
    "Üretim ortamında {Keyword}",
    "{Keyword} performansını optimize etme",
    "{Keyword} kullanım senaryoları",
    "{Keyword} yaklaşımlarını karşılaştırma",
]

MUST_COVER_INTRO: list[str] = [
    "{keyword} kavramını tanımla",
    "Şu an neden önemli olduğu",
    "Bu yazının kime yönelik olduğu",
]
MUST_COVER_CORE: list[str] = [
    "{keyword} ile ilgili temel kavram",
    "Pratik uygulama",
    "Örnek veya vaka",
]
MUST_COVER_TOPIC: list[str] = [
    "{topic} konusunun {keyword} içindeki rolünü açıkla",
    "Somut örnekler",
    "Sık karşılaşılan tuzaklar",
]
MUST_COVER_SUMMARY: list[str] = [
    "Ana çıkarımlar",
    "Okuyucunun atacağı bir sonraki adım",
]

IMAGE_ALT_TEMPLATES: dict[str, str] = {
    "filename": "{stem}",
    "keyword_with_stem": "{keyword} — {stem}",
    "keyword_with_topic": "{keyword}: {topic}",
    "topic_only": "{topic}",
}

H2_STYLE_TEMPLATES: dict[str, str] = {
    "question": "{base} nedir?",
    "imperative": "{base} öğren",
    "statement": "{base}",
    "mixed": "{base}",
}

SUMMARY_H2: dict[str, str] = {
    "question": "Bundan sonra {keyword} ile ne yapmalısınız?",
    "imperative": "{keyword} pratiğe geçirin",
    "statement": "{keyword}: ana çıkarımlar",
    "mixed": "{keyword}: ana çıkarımlar",
}

TOPIC_CONNECTOR = "ve"
