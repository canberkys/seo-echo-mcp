# seo-echo-mcp — Build Specification

> **Kullanım:** Yeni bir boş klasör aç (örn: `mkdir seo-echo-mcp && cd seo-echo-mcp`), Claude Code oturumu başlat (`claude`), bu dosyanın **tüm içeriğini** kopyala, ilk prompt olarak yapıştır. Claude Code önce plan çıkaracak, sonra tüm dosyaları oluşturacak.

---

## 0. Proje özeti

**Ne?** `seo-echo-mcp`, bir blog'un mevcut içerik stilini çıkarıp, o stile uygun SEO-optimize içerik üretim sürecini destekleyen bir MCP sunucusudur. Açık kaynak (MIT), Python bazlı, PyPI üzerinden `uvx seo-echo-mcp` ile kurulur.

**Kim için?** Bloggerlar, içerik pazarlamacıları, solo founder'lar. Claude Code, Cursor, Windsurf, Claude Desktop, Zed, VS Code (Copilot) dahil tüm MCP-uyumlu IDE'lerde çalışır.

**Farkı?** Mevcut SEO MCP'leri (egebese/seo-research, dataforseo, ahrefs) hep **veri** tarafında. Bu MCP **voice preservation** ekseninde konumlanıyor: "Senin sesinde, senin kategorilerinde, SEO-uyumlu içerik yazmayı kolaylaştır."

**Dil-bağımsız.** Tüm tool'lar site profilinden dili tespit eder, o dilde çalışır. Hardcoded Türkçe/İngilizce yok.

**MCP'nin yapmayacağı:** Tam yazının kendisini üretmek. Bu host LLM'in işi. MCP yapı, analiz ve denetim sağlar.

---

## 1. Genel prensipler

- **Stateless tool'lar:** Her tool input alıp output verir, dosya sistemine state kaydetmez. State'i host LLM (Claude Code vs.) yönetir.
- **Harici API bağımlılığı opsiyonel:** Core tool'lar (analyze_site, audit_content) hiçbir API key olmadan çalışır. SERP analizi için DuckDuckGo (ücretsiz) default, Google Custom Search/Ahrefs opsiyonel.
- **Dil-bağımsız:** Kod İngilizce (docstring + yorum + log). Girdi/çıktı verisi kullanıcının dilinde.
- **Type-safe:** Her tool Pydantic modellerle input/output şemalarını tanımlar.
- **Python 3.10+**, async tercih edilir (httpx.AsyncClient).
- **Open source best practice:** Type hints, docstring, test coverage >70%, GitHub Actions CI.

---

## 2. Tech Stack

| Katman | Araç | Sürüm | Neden |
|---|---|---|---|
| Language | Python | 3.10+ | MCP ekosistemi standart |
| MCP Framework | `fastmcp` | 0.2+ | Decorator-based, kısa ve temiz |
| HTTP | `httpx` | 0.27+ | Async, HTTP/2 |
| HTML Parse | `selectolax` | 0.3+ | BS4'ten çok daha hızlı |
| Main Content | `trafilatura` | 1.12+ | Industry standard, multilingual |
| Language Detect | `py3langid` | 0.2+ | Hafif, offline, 97 dil |
| Schemas | `pydantic` | 2.0+ | Type-safe I/O |
| Package Mgmt | `uv` | latest | Hız |
| Testing | `pytest` + `pytest-asyncio` | latest | Standard |
| Linter | `ruff` | latest | Hız + format |
| Dist | `hatchling` build backend | latest | `uv` ile iyi çalışır |

---

## 3. Proje yapısı

```
seo-echo-mcp/
├── .github/
│   └── workflows/
│       ├── test.yml
│       └── publish.yml
├── src/
│   └── seo_echo_mcp/
│       ├── __init__.py
│       ├── server.py                    # FastMCP entry point
│       ├── schemas.py                   # Pydantic models
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── analyze_site.py
│       │   ├── analyze_competitors.py
│       │   ├── generate_outline.py
│       │   └── audit_content.py
│       ├── extractors/
│       │   ├── __init__.py
│       │   ├── sitemap.py               # Sitemap/feed discovery
│       │   ├── content.py               # Trafilatura wrapper
│       │   ├── style.py                 # Style heuristics
│       │   └── serp.py                  # DuckDuckGo HTML scrape
│       └── config/
│           ├── __init__.py
│           ├── ai_cliches.py            # Multi-language AI cliché lists
│           └── seo_rules.py             # SEO scoring rules
├── tests/
│   ├── __init__.py
│   ├── test_analyze_site.py
│   ├── test_audit_content.py
│   ├── test_extractors.py
│   └── fixtures/
│       └── sample_sitemap.xml
├── .gitignore
├── .python-version                      # 3.10
├── LICENSE                              # MIT
├── README.md
├── CHANGELOG.md
├── pyproject.toml
└── uv.lock                              # Generated, gitignored initially
```

---

## 4. Tool spesifikasyonları

### Tool 1: `analyze_site`

**Amaç:** Verilen blog URL'sinden site profilini çıkarır. Bu profil diğer tüm tool'lara `site_profile` olarak geçirilir.

**İmza:**
```python
@mcp.tool()
async def analyze_site(
    url: str,
    max_samples: int = 12,
) -> SiteProfile:
    ...
```

**Input:**
- `url` (str, required): Blog ana sayfa URL'si. Protokol otomatik normalize edilir.
- `max_samples` (int, default 12): Maksimum kaç yazı örneklenecek.

**Output: `SiteProfile`**
```python
class PostSample(BaseModel):
    url: str
    title: str
    h2s: list[str]
    word_count: int
    category: str | None
    snippet: str  # First 200 chars of main content
    published_at: str | None  # ISO date if detected

class StyleProfile(BaseModel):
    average_word_count: int
    tone: Literal["formal", "informal", "technical", "conversational", "journalistic", "mixed"]
    addressing: str  # sen, siz, you, tu, vous, du, sie, etc.
    h2_pattern: Literal["question", "statement", "imperative", "mixed"]
    uses_lists: bool
    uses_code_blocks: bool
    avg_paragraph_sentences: float
    em_dash_frequency: Literal["frequent", "occasional", "rare", "never"]
    avg_sentence_words: float

class SiteProfile(BaseModel):
    domain: str
    url: str
    language: str  # ISO 639-1 (tr, en, fr, de, etc.)
    language_confidence: Literal["high", "medium", "mixed"]
    sampled_at: str  # ISO datetime
    sample_count: int
    sample_urls: list[str]
    categories: list[str]  # Top 3-5 detected categories
    topics: list[str]  # Top 5-8 detected topic keywords
    style: StyleProfile
    existing_posts: list[PostSample]
```

**Davranış sırası:**

1. **URL normalize:** Protokol yoksa `https://` ekle, trailing `/` kaldır.
2. **Discovery:** `extractors.sitemap.discover_posts(url)` çağır. Bu fonksiyon şu sırayla dener:
   - `{url}/sitemap.xml`
   - `{url}/sitemap_index.xml`
   - `{url}/wp-sitemap.xml`
   - `{url}/feed/`, `/rss.xml`, `/atom.xml`
   - Ana sayfa + blog index parsing (son çare)
3. **Sample selection:** Bulunan URL'lerden `max_samples` kadar seç. Strateji: `lastmod` varsa en yeni 50% + kategori çeşitliliği için kalan 50%.
4. **Parallel fetch:** `httpx.AsyncClient` ile concurrent (max 5 eşzamanlı) tüm örnekleri çek.
5. **Her post için:**
   - `trafilatura.extract()` ile ana metin çıkar
   - `selectolax` ile H2'leri ve meta tag'leri parse et
   - Word count, snippet (ilk 200 char)
   - Kategori tahmin: breadcrumb → meta tag → URL path
6. **Language detection:** Tüm örneklerden toplanan metne `py3langid.classify()` uygula. `language_confidence`:
   - Tek dil, %90+ → "high"
   - Baskın dil %70-90 → "medium"
   - Karışık → "mixed"
7. **Style analysis:** `extractors.style.analyze()` çalıştır:
   - Tone: Cümle uzunluğu, jargon yoğunluğu, pronoun pattern'den heuristic
   - Addressing: Pronoun frekans analizi (language-aware config)
   - H2 pattern: Soru işareti oranı, imperative verb oranı
   - em_dash_frequency: Toplam em-dash / toplam yazı
8. **Return:** Tüm alanları doldurulmuş `SiteProfile`.

**Hata durumları:**
- URL erişilemez → `ValueError("Unable to reach URL: {url}")`
- Hiç post bulunamadı → `ValueError("Could not discover any posts. Provide URLs manually via ...")` — daha sonra v0.2'de manual URL list parametresi ekleriz
- Tüm örnekler boş içerik → `ValueError("Posts found but content extraction failed. Site may be JS-rendered.")`

**Notlar:**
- Rate limit için host başına 500ms delay
- User-Agent: `seo-echo-mcp/{version} (+https://github.com/{user}/seo-echo-mcp)`
- Timeout: per-request 15s, total 3 dakika

---

### Tool 2: `analyze_competitors`

**Amaç:** Bir keyword için top SERP sonuçlarını alır veya verilen URL'leri analiz eder. Rakiplerin H2 yapısını, ortalama kelime sayısını, format trendlerini çıkarır.

**İmza:**
```python
@mcp.tool()
async def analyze_competitors(
    keyword: str | None = None,
    urls: list[str] | None = None,
    language: str = "en",
    country: str = "us",
    top_n: int = 10,
) -> CompetitorAnalysis:
    ...
```

**Input:**
- `keyword` (str, optional): SERP araması yapılacak keyword. `urls` verilmezse zorunlu.
- `urls` (list[str], optional): Direkt verilen URL listesi (SERP araması atlanır).
- `language` (str): ISO 639-1. SERP aramasına etki eder.
- `country` (str): ISO 3166-1 alpha-2.
- `top_n` (int, default 10): Kaç sonuç analiz edilecek.

**Output: `CompetitorAnalysis`**
```python
class SerpEntry(BaseModel):
    url: str
    title: str
    position: int
    snippet: str
    h2s: list[str]
    word_count: int
    has_schema: bool
    schema_types: list[str]  # Article, FAQPage, HowTo, etc.
    internal_link_count: int
    external_link_count: int

class CompetitorInsights(BaseModel):
    average_word_count: int
    word_count_range: tuple[int, int]
    common_h2_topics: list[str]  # Top 5-8 across all competitors
    dominant_format: Literal["listicle", "guide", "comparison", "tutorial", "review", "news", "mixed"]
    title_patterns: list[str]  # e.g. "How to X", "Best X for Y"
    schema_adoption_pct: float  # 0.0-1.0
    avg_internal_links: int
    avg_external_links: int

class CompetitorAnalysis(BaseModel):
    keyword: str | None
    language: str
    country: str
    fetched_at: str
    results: list[SerpEntry]
    insights: CompetitorInsights
```

**Davranış:**

1. **SERP discovery:** `urls` verildiyse → skip. Yoksa `extractors.serp.duckduckgo_search(keyword, language, country, top_n)` çağır.
2. **Parallel fetch:** Her URL için concurrent fetch (max 5).
3. **Her sonuç için:**
   - Trafilatura ile content
   - H2 extraction
   - Schema.org JSON-LD detection (içeride `<script type="application/ld+json">` var mı, hangi `@type`'lar?)
   - Link sayımı: `a[href]` sayısı, internal (aynı domain) vs external
4. **Insights aggregation:**
   - Word count ortalama + range
   - Common H2 topics: Tüm H2'leri tokenize et, keyword extraction (basit TF)
   - Dominant format: Title + H2 pattern'lardan tahmin (listicle = "N X"/"N best", guide = "how to"/"ultimate", vs.)
   - Title pattern: Regex-based template detection
5. **Return** `CompetitorAnalysis`.

**DuckDuckGo scraping notu:**
- Endpoint: `https://html.duckduckgo.com/html/?q={query}&kl={country}-{language}`
- CSS selector: `.result__a` → href, title
- Rate limit riski var; başarısız olursa fallback: Bing HTML
- User gerçekten ciddi bir şey yapıyorsa kendisi Google Custom Search API key ekleyebilir — env var `GOOGLE_CSE_API_KEY` + `GOOGLE_CSE_ID` varsa onu kullan (opsiyonel branch).

---

### Tool 3: `generate_outline`

**Amaç:** Site profiline ve rakip analizine göre yazı outline'ı üretir. Outline'daki H2'ler site'ın pattern'ine uyum sağlar, kelime sayısı hedefi site ortalamasını takip eder.

**İmza:**
```python
@mcp.tool()
async def generate_outline(
    keyword: str,
    site_profile: SiteProfile,
    competitor_analysis: CompetitorAnalysis | None = None,
    target_word_count: int | None = None,
    new_category: str | None = None,
) -> Outline:
    ...
```

**Input:**
- `keyword` (str): Hedef keyword.
- `site_profile` (dict): `analyze_site` çıktısı.
- `competitor_analysis` (optional): `analyze_competitors` çıktısı. Yoksa outline daha jenerik olur.
- `target_word_count` (optional): Belirtilmezse `site_profile.style.average_word_count` kullanılır.
- `new_category` (optional): Yeni kategori belirtilirse outline o bağlamda üretilir.

**Output: `Outline`**
```python
class OutlineSection(BaseModel):
    h2: str
    purpose: str  # "Introduction", "Core explanation", "Comparison", "CTA"
    word_count_target: int
    must_cover: list[str]  # 2-4 key points
    suggested_visuals: list[str]  # "diagram", "comparison table", "screenshot"

class Outline(BaseModel):
    keyword: str
    language: str
    suggested_titles: list[str]  # Exactly 3
    suggested_meta_descriptions: list[str]  # Exactly 3, each 140-160 chars
    word_count_target: int
    h2_style: str  # Inherited from site_profile
    addressing: str  # Inherited from site_profile
    category: str  # Either from site or new_category
    sections: list[OutlineSection]
    recommended_internal_link_targets: list[str]  # URL'ler, site_profile.existing_posts'tan seç
    external_citation_topics: list[str]  # "recent statistics on X", "study about Y"
    cta_suggestion: str
```

**Davranış (tamamen kural-tabanlı, LLM çağrısı YOK):**

1. **Section count hesapla:** `target_word_count // 250` → minimum 5, maksimum 12.
2. **H2 başlıkları için pattern:** `site_profile.style.h2_pattern` ne ise ona göre format:
   - `question` → "X nedir?", "X nasıl çalışır?", "X neden önemlidir?" vb. (dile göre template)
   - `statement` → Declarative başlıklar
   - `imperative` → "X yap", "Y'yi öğren" formatı
3. **Section purpose sıralaması (universal):**
   - Section 1: Introduction (keyword tanımı + neden önemli)
   - Section 2-3: Foundational concepts
   - Section 4-N-2: Core content (competitor H2'lerden en sık geçenler)
   - Section N-1: Practical application / examples
   - Section N: Summary + CTA
4. **Competitor H2 topic'lerini dağıt:** `competitor_analysis.insights.common_h2_topics` varsa, bu topic'leri middle section'lara map et.
5. **Title generation (3 adet):** Competitor title pattern'larını kullanarak template fill. Template'ler dile göre `config/title_templates.py`'den gelsin.
6. **Meta description generation (3 adet):** 140-160 karakter, pattern: "Problem → Value → Qualifier". Template-based.
7. **Internal link targets:** `site_profile.existing_posts`'tan keyword-relevant 3-5 tane seç (basit keyword matching).
8. **External citation topics:** Section içeriğine göre generic prompt'lar: "Recent 2025-2026 statistics on X".
9. **CTA suggestion:** Dile göre template, örnek: "Subscribe to newsletter for more X", "Try our Y tool".

**Notlar:**
- Title ve meta description template'leri **dile göre ayrı dosyalarda** tutulsun: `config/templates/tr.py`, `config/templates/en.py`, `config/templates/es.py`, vb. Başlangıçta `tr`, `en`, `es`, `fr`, `de` için destek. Fallback: `en`.
- Outline'ı host LLM'e verip yazı yazdıracağız, yani outline net ve parametrik olmalı.

---

### Tool 4: `audit_content`

**Amaç:** Yazılan markdown içeriği site profiline ve SEO kurallarına göre denetler. Skor + düzeltilmesi gereken noktaları döndürür.

**İmza:**
```python
@mcp.tool()
async def audit_content(
    content_markdown: str,
    site_profile: SiteProfile,
    target_keyword: str | None = None,
    target_meta_description: str | None = None,
) -> AuditReport:
    ...
```

**Input:**
- `content_markdown` (str): Frontmatter + body. Frontmatter opsiyonel.
- `site_profile` (dict): Stil karşılaştırması için.
- `target_keyword` (optional): Keyword-specific checks için.
- `target_meta_description` (optional): Meta description validation için.

**Output: `AuditReport`**
```python
class Check(BaseModel):
    name: str
    pass_: bool  # Python'da `pass` reserved, alias
    severity: Literal["error", "warning", "info"]
    actual: str | int | float | list | None
    expected: str | int | float | None
    message: str

class AuditReport(BaseModel):
    overall_score: int  # 0-100
    passed_count: int
    warning_count: int
    error_count: int
    checks: list[Check]
    recommendations: list[str]  # Prioritized action items
    reading_time_minutes: int
    word_count: int
    detected_language: str
```

**Davranış — Check listesi (hepsi rule-based):**

1. **word_count** — `site_profile.style.average_word_count`'un ±%25 aralığında mı? Dışındaysa warning.
2. **h2_format** — H2'lerin %70+'ı `site_profile.style.h2_pattern`'e uyuyor mu? Değilse error.
3. **em_dash_usage** — `site_profile.style.em_dash_frequency` "never" ise em-dash sayısı >0 → error. "rare" ise >5 → warning.
4. **ai_cliches** — `config.ai_cliches` içindeki dildeki liste ile match yap. Her hit bir warning, ilk 5'i recommendations'a eklensin.
5. **addressing_consistency** — Tespit edilen addressing `site_profile.style.addressing` ile aynı mı?
6. **keyword_in_title** — `target_keyword` title'da (H1 veya ilk satır) geçiyor mu?
7. **keyword_density** — Body içinde `target_keyword` geçiş sayısı / toplam kelime. %0.5-2.0 arası ideal. Dışındaysa warning.
8. **keyword_in_first_paragraph** — İlk paragrafta target_keyword var mı?
9. **internal_links_count** — Markdown'da internal link (aynı domain) sayısı >=3 mi?
10. **external_citations_count** — External link sayısı >=3 mi?
11. **meta_description_length** — `target_meta_description` varsa 140-160 arasında mı?
12. **headings_hierarchy** — H1 tek, H3 öncesi H2 var, atlamalı hiyerarşi yok.
13. **paragraph_length** — Ortalama paragraf cümle sayısı `site_profile.style.avg_paragraph_sentences`'a uyumlu mu (±2)?
14. **sentence_length** — Ortalama cümle kelime sayısı `site_profile.style.avg_sentence_words`'e uyumlu mu (±5)?
15. **image_alt_coverage** — Tüm `![alt](url)` formatlı imajlarda alt text var mı? (Boş `![](url)` hata)
16. **reading_time** — `word_count / 200` dakika.

**Overall score hesabı:**
- Her check severity'sine göre ağırlık: error=10, warning=3, info=1
- `score = 100 - (sum of failed weights)` → min 0.

**Recommendations:**
- En yüksek severity failed check'leri için action item üret. Dile göre template'lerden.

---

## 5. Dosya içerikleri

### 5.1 `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "seo-echo-mcp"
version = "0.1.0"
description = "MCP server that analyzes your blog's voice and helps create SEO content that matches your style — language-agnostic."
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [
    { name = "YOUR_NAME", email = "YOUR_EMAIL" }
]
keywords = [
    "seo",
    "mcp",
    "model-context-protocol",
    "content",
    "writing-style",
    "blog",
    "voice",
    "seo-tools",
    "content-optimization",
    "llm-tools",
    "ai-writing"
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Text Processing",
]
dependencies = [
    "fastmcp>=0.2.0",
    "httpx>=0.27.0",
    "selectolax>=0.3.21",
    "trafilatura>=1.12.0",
    "py3langid>=0.2.2",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.6.0",
    "respx>=0.21.0",  # httpx mock
]

[project.scripts]
seo-echo-mcp = "seo_echo_mcp.server:main"

[project.urls]
Homepage = "https://github.com/YOUR_USER/seo-echo-mcp"
Issues = "https://github.com/YOUR_USER/seo-echo-mcp/issues"
Changelog = "https://github.com/YOUR_USER/seo-echo-mcp/blob/main/CHANGELOG.md"

[tool.hatch.build.targets.wheel]
packages = ["src/seo_echo_mcp"]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "N", "SIM"]
ignore = ["E501"]  # line too long (handled by formatter)

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### 5.2 `LICENSE`

Standart MIT lisansı. `YEAR` ve `AUTHOR_NAME` placeholder kullan.

```
MIT License

Copyright (c) 2026 YOUR_NAME

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 5.3 `src/seo_echo_mcp/server.py`

FastMCP entry point. Her tool ayrı dosyadan import edilip register edilir.

**İçerik mantığı:**
```python
"""seo-echo-mcp: Voice-preserving SEO content MCP server."""

from fastmcp import FastMCP

from seo_echo_mcp.tools.analyze_site import analyze_site as _analyze_site
from seo_echo_mcp.tools.analyze_competitors import analyze_competitors as _analyze_competitors
from seo_echo_mcp.tools.generate_outline import generate_outline as _generate_outline
from seo_echo_mcp.tools.audit_content import audit_content as _audit_content

mcp = FastMCP(
    name="seo-echo-mcp",
    version="0.1.0",
    description="Voice-preserving SEO content MCP server"
)

# Register tools
mcp.tool()(_analyze_site)
mcp.tool()(_analyze_competitors)
mcp.tool()(_generate_outline)
mcp.tool()(_audit_content)


def main():
    """CLI entry point for stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
```

### 5.4 `src/seo_echo_mcp/schemas.py`

Tüm Pydantic modelleri burada. Tool dosyaları buradan import eder. Yukarıdaki tool spec'lerinde verilen modeller aynen kullanılır.

### 5.5 `src/seo_echo_mcp/tools/*.py`

Her tool kendi dosyasında. Davranış mantığı yukarıda detaylı. Her dosya:
- Docstring (tool purpose, args, returns)
- Type-hinted async function
- Argument validation
- Orchestration logic (extractor çağrıları)
- Error handling

### 5.6 `src/seo_echo_mcp/extractors/*.py`

**sitemap.py:** `discover_posts(url) -> list[str]` — yukarıda açıklanan fallback chain.

**content.py:** `extract_content(html) -> dict` — trafilatura wrapper, döndürür: `{title, main_text, word_count, h2s}`.

**style.py:** `analyze_style(texts: list[str], language: str) -> StyleProfile` — heuristic analiz.

**serp.py:** `duckduckgo_search(query, language, country, top_n) -> list[dict]` — HTML scrape.

### 5.7 `src/seo_echo_mcp/config/ai_cliches.py`

Dile göre AI klişeleri. Her dil için liste. Başlangıçta minimum Türkçe, İngilizce, İspanyolca, Fransızca, Almanca:

```python
AI_CLICHES: dict[str, list[str]] = {
    "tr": [
        "dijital çağda", "günümüz dünyasında", "günümüzde", "sonuç olarak",
        "özetle", "kapsamlı bir şekilde", "detaylıca inceledik", "derinlemesine",
        "hızla değişen dünyada", "teknolojinin ilerlemesiyle", "adeta",
        "söz konusu olduğunda", "ele aldık",
    ],
    "en": [
        "in today's digital age", "in the modern era", "at the end of the day",
        "it's worth noting", "it goes without saying", "in conclusion",
        "to sum up", "delve into", "tapestry", "realm", "landscape",
        "in this comprehensive guide", "embark on a journey",
    ],
    "es": [
        "en la era digital", "en el mundo actual", "en conclusión",
        "profundizar en", "a fin de cuentas", "cabe destacar",
    ],
    "fr": [
        "à l'ère numérique", "dans le monde d'aujourd'hui", "en conclusion",
        "il est important de noter", "approfondir", "en fin de compte",
    ],
    "de": [
        "im digitalen zeitalter", "in der heutigen welt", "abschließend",
        "es ist wichtig zu beachten", "eintauchen in",
    ],
}
```

Topluluk PR'larla genişletilebilecek şekilde dokümante et.

### 5.8 `src/seo_echo_mcp/config/seo_rules.py`

SEO scoring rule'ları. Word count aralığı, keyword density hedefi, internal link minimum, meta description uzunluk bounds. Tek dosya, kolay değiştirilebilir.

### 5.9 `README.md`

Şu yapıda yaz (mevcut başarılı MCP repo'ları takip ediyor):

```markdown
# seo-echo-mcp

**Voice-preserving SEO content MCP server — language-agnostic.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)]
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)]
[![PyPI](https://img.shields.io/pypi/v/seo-echo-mcp)]

[Features](#features) • [Installation](#installation) • [IDE Setup](#ide-setup) • [API Reference](#api-reference) • [Contributing](#contributing)

---

## 🎯 What is this?

Most SEO MCPs give you keyword data. **seo-echo-mcp is different:** it reads your existing blog, extracts your writing voice, and makes sure new SEO content matches that voice — in any language.

Think of it as giving your LLM assistant a "style mirror" for your content.

## ✨ Features

| Tool | What it does |
|---|---|
| `analyze_site` | Crawls your blog, extracts language, topics, style profile, H2 patterns |
| `analyze_competitors` | Fetches top SERP results for a keyword and extracts their structure |
| `generate_outline` | Produces an SEO-optimized outline that matches your site's voice |
| `audit_content` | Scores a draft against your style profile + SEO best practices |

## 🌍 Language support

Works with **any language** that has ISO 639-1 code. Built-in AI cliché detection for: Turkish, English, Spanish, French, German (contributions welcome for more).

## 📦 Installation

### Via PyPI (recommended)
\`\`\`bash
pip install seo-echo-mcp
# or
uv pip install seo-echo-mcp
\`\`\`

### Via uvx (no install)
Configure your IDE to run `uvx seo-echo-mcp` directly.

## 🛠️ IDE Setup

[Her IDE için aynı config template — egebese'nin formatını takip et: Claude Code, Claude Desktop, Cursor, Windsurf, VS Code, Zed]

### Claude Code
\`\`\`bash
claude mcp add seo-echo --scope user -- uvx seo-echo-mcp
\`\`\`

### Claude Desktop
`claude_desktop_config.json`:
\`\`\`json
{
  "mcpServers": {
    "seo-echo": {
      "command": "uvx",
      "args": ["seo-echo-mcp"]
    }
  }
}
\`\`\`

### Cursor
`.cursor/mcp.json`:
\`\`\`json
{
  "mcpServers": {
    "seo-echo": {
      "command": "uvx",
      "args": ["seo-echo-mcp"]
    }
  }
}
\`\`\`

[... diğer IDE'ler ...]

## 📖 API Reference

[Her tool için: açıklama, parametreler, örnek çıktı — Pydantic şema JSON örneği göster]

## 💡 Usage examples

[Example 1: Full workflow — analyze your site, research keyword, generate outline, audit draft]
[Example 2: Multi-language — Turkish blog, Spanish blog]
[Example 3: Combining with egebese for Ahrefs data]

## 🤝 Contributing

Contributions welcome! See CONTRIBUTING.md.

**Adding a language to AI cliché detection:** edit `src/seo_echo_mcp/config/ai_cliches.py`, add your language code and list of phrases, submit PR.

## 📊 Roadmap

- [ ] v0.2: Google Custom Search API integration
- [ ] v0.2: Persistent cache for analyze_site
- [ ] v0.3: Schema.org JSON-LD generator tool
- [ ] v0.3: Image alt text analyzer
- [ ] v0.4: Multi-site profile support

## 📄 License

MIT — see [LICENSE](LICENSE).

## 🙏 Credits

Inspired by [egebese/seo-research-mcp](https://github.com/egebese/seo-research-mcp) (keyword data) and [tiagolemos05/claude-mcps-and-prompts](https://github.com/tiagolemos05/claude-mcps-and-prompts) (workflow patterns).
```

### 5.10 `CHANGELOG.md`

```markdown
# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] — 2026-04-21

### Added
- Initial release
- `analyze_site` tool: blog crawling + profile extraction
- `analyze_competitors` tool: SERP analysis via DuckDuckGo
- `generate_outline` tool: voice-preserving outline generation
- `audit_content` tool: rule-based content scoring
- Language support: Turkish, English, Spanish, French, German
```

### 5.11 `.gitignore`

Standard Python + venv + IDE artifacts. `uv.lock` **INCLUDE** (lock file for reproducibility).

```
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/
.venv/
venv/
.env
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
.vscode/
.idea/
*.swp
.DS_Store
```

### 5.12 `.python-version`

```
3.10
```

### 5.13 `.github/workflows/test.yml`

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - name: Set up Python
        run: uv python install ${{ matrix.python-version }}
      - name: Install dependencies
        run: uv sync --extra dev
      - name: Lint
        run: uv run ruff check
      - name: Test
        run: uv run pytest --cov=seo_echo_mcp --cov-report=term-missing
```

### 5.14 `.github/workflows/publish.yml`

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: release
    permissions:
      id-token: write  # OIDC for PyPI trusted publishing
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv build
      - uses: pypa/gh-action-pypi-publish@release/v1
```

### 5.15 `tests/`

Her tool için en az 2-3 smoke test. Örnek yapı:

**tests/test_analyze_site.py:**
```python
import pytest
from seo_echo_mcp.tools.analyze_site import analyze_site

@pytest.mark.asyncio
async def test_analyze_site_returns_profile_for_valid_url(respx_mock):
    # Mock sitemap + sample posts
    # Assert SiteProfile structure
    ...

@pytest.mark.asyncio
async def test_analyze_site_raises_on_unreachable_url():
    ...

@pytest.mark.asyncio
async def test_analyze_site_detects_turkish_language():
    ...
```

**tests/test_audit_content.py:**
```python
def test_audit_detects_em_dashes_when_profile_says_never():
    ...

def test_audit_catches_ai_cliches_in_turkish():
    ...

def test_audit_score_calculation():
    ...
```

**tests/test_extractors.py:** Sitemap parsing, DuckDuckGo parsing edge cases.

---

## 6. İmplementasyon sırası (Claude Code için)

Bu sırayla çalış:

1. **Scaffold:** Tüm klasörleri ve boş dosyaları oluştur. `pyproject.toml`, `LICENSE`, `.gitignore`, `.python-version`, `README.md`, `CHANGELOG.md`.
2. **Dependencies kur:** `uv init --lib` ile init et (yukarıdaki pyproject.toml ile override et), sonra `uv sync --extra dev`.
3. **Schemas yaz:** `src/seo_echo_mcp/schemas.py` — tüm Pydantic modeller. Diğer modüller buna bağlı.
4. **Extractors yaz:**
   - `sitemap.py` (discovery)
   - `content.py` (trafilatura wrapper)
   - `style.py` (heuristic analysis)
   - `serp.py` (DuckDuckGo)
5. **Config yaz:** `ai_cliches.py`, `seo_rules.py`, dil bazlı template'ler.
6. **Tool'ları yaz (sırayla):**
   - `analyze_site` (en kolay, extractors'ı tetikler)
   - `audit_content` (rule-based, LLM/SERP gerekmiyor)
   - `analyze_competitors` (SERP + fetch)
   - `generate_outline` (en kompleks, diğer tool output'larına bağlı)
7. **Server register:** `server.py`.
8. **Tests:** Her tool için en az 1 smoke test.
9. **CI yaml'ları:** `.github/workflows/`.
10. **README:** Placeholder'ları `YOUR_USER`, `YOUR_NAME` olarak bırak, kullanıcı sonra kendi bilgileriyle değiştirsin.
11. **Smoke run:** `uv run seo-echo-mcp` ile server başlatılabiliyor mu kontrol et (stdio ping testi opsiyonel).

---

## 7. Test stratejisi

- **Unit:** Extractors için mock'lu testler (respx ile httpx mock).
- **Integration:** `analyze_site` için fixture sitemap dosyası + mock HTTP responses.
- **Lint + format:** `ruff check` + `ruff format` zorunlu, CI'da fail.
- **Coverage hedefi:** v0.1 için %60+, v1.0 için %80+.

---

## 8. Publishing workflow

1. Local: `uv build` → wheel ve sdist oluşur.
2. Test PyPI'ya ilk deneme: `uv publish --index testpypi`.
3. GitHub'da repo oluştur, push.
4. PyPI'da `seo-echo-mcp` ismini reserve et (boş project yükleyerek).
5. PyPI Trusted Publishing konfigüre et (GitHub Actions OIDC). Repo owner ayarı gerekli, kullanıcı elle yapar.
6. İlk release: Git tag `v0.1.0` + GitHub Release → `publish.yml` otomatik PyPI'ya yükler.

---

## 9. Son checklist

Kurulum tamamlandığında şunların var olduğunu doğrula:

- [ ] `src/seo_echo_mcp/` altında 4 tool dosyası, schemas.py, server.py
- [ ] `extractors/` 4 dosya
- [ ] `config/` içinde ai_cliches.py ve seo_rules.py
- [ ] `tests/` içinde her tool için en az 1 test
- [ ] `pyproject.toml` yukarıdaki içerikle birebir
- [ ] `LICENSE` MIT, yıl 2026
- [ ] `README.md` placeholder'larıyla dolu, 6+ IDE setup section'ı var
- [ ] `CHANGELOG.md` v0.1.0 entry'si var
- [ ] `.github/workflows/` altında test.yml ve publish.yml
- [ ] `uv sync --extra dev` hatasız çalışıyor
- [ ] `uv run ruff check` temiz
- [ ] `uv run pytest` tüm testler geçiyor
- [ ] `uv run seo-echo-mcp` server başlıyor (stdio'da beklemesi normal)

---

## 10. Kullanıcıya son mesaj

Her şey hazırlandığında şu mesajı ver:

```
🎉 seo-echo-mcp v0.1.0 scaffolding tamam.

📁 Proje yapısı kuruldu: 4 tool, 4 extractor, 2 config, CI/CD workflows.
🧪 Test çalıştırmak için: uv run pytest
🚀 Local olarak denemek için: uv run seo-echo-mcp (stdio'da bekler, normal)

Kullanıcıya düşen:
1. README.md'de YOUR_USER, YOUR_NAME, YOUR_EMAIL placeholder'larını değiştir
2. GitHub'da repo oluştur, push
3. PyPI'da proje kaydı ve Trusted Publishing kur
4. İlk release için git tag + GitHub Release

Sorularını yönlendirmek için CONTRIBUTING.md de eklemek istersen söyle, hazırlayayım.
```

---

Şimdi başla: adım adım, sırayla, hiçbir dosyayı atlamadan.
