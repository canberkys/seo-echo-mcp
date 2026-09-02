"""Smoke tests for readability_report."""

from __future__ import annotations

import pytest

from seo_echo_mcp.tools.readability_report import readability_report


@pytest.mark.asyncio
async def test_readability_english_easy_short_sentences():
    draft = "# Title\n\nThis is fun. Cats are nice. Dogs run fast. We like them all."
    report = await readability_report(draft, language="en")
    assert report.formula_used == "flesch-en"
    assert report.verdict in ("easy", "medium")
    assert report.avg_sentence_words > 0
    assert report.passive_voice_ratio is not None


@pytest.mark.asyncio
async def test_readability_english_hard_long_sentences():
    draft = (
        "# Title\n\n"
        "The implementation of sophisticated distributed consensus algorithms "
        "requires comprehensive understanding of Byzantine fault tolerance "
        "mechanisms, which fundamentally underpin modern infrastructure."
    )
    report = await readability_report(draft, language="en")
    assert report.formula_used == "flesch-en"
    assert report.avg_sentence_words > 15


@pytest.mark.asyncio
async def test_readability_turkish_uses_atesman():
    draft = "# Başlık\n\nBu kısa bir örnek. Cümleler sade. Okuması kolay. Türkçe formülü denenir."
    report = await readability_report(draft, language="tr")
    assert report.formula_used == "atesman-tr"
    # TR passive voice detection is active; no passives in this sample → 0.0.
    assert report.passive_voice_ratio == 0.0


@pytest.mark.asyncio
async def test_readability_fallback_formula():
    draft = "# Başlık\n\n" + "Kısa cümle. " * 5
    report = await readability_report(draft, language="pl")
    assert report.formula_used == "generic"


@pytest.mark.asyncio
async def test_readability_tr_passive_voice_detected():
    draft = (
        "# Başlık\n\nSanal makine taşındı ve yeni host'a bağlandı. "
        "İşlem başarıyla tamamlandı ve raporlar gönderildi."
    )
    report = await readability_report(draft, language="tr")
    assert report.passive_voice_ratio is not None
    assert report.passive_voice_ratio > 0


@pytest.mark.asyncio
async def test_readability_de_passive_voice_detected():
    draft = (
        "# Titel\n\nDie Daten werden gesichert und der Server wurde neu gestartet. "
        "Das System wird konfiguriert."
    )
    report = await readability_report(draft, language="de")
    assert report.passive_voice_ratio is not None
    assert report.passive_voice_ratio > 0


@pytest.mark.asyncio
async def test_readability_tr_active_past_low_passive_ratio():
    """Active-voice Turkish past-tense narrative should score close to zero passive.

    The regex is approximate — verbs with -in-/-il- that are reflexive/middle
    voice (sevindi, yanıldı) may match. We require ratio < 1.0 to guard against
    catastrophic over-matching while accepting some noise.
    """
    draft = (
        "# Başlık\n\n"
        "Dün akşam raporu yazdım ve ekibe gönderdim. "
        "Sabah tekrar baktım, bir hata gördüm. "
        "Düzelttim ve onayladım. Sonra bir kahve içtim."
    )
    report = await readability_report(draft, language="tr")
    assert report.passive_voice_ratio is not None
    # Known active past-tense sentences; passive heuristic should be low.
    assert report.passive_voice_ratio < 1.0, (
        f"active-voice text flagged too high: ratio={report.passive_voice_ratio}"
    )


@pytest.mark.asyncio
async def test_readability_de_active_low_passive_ratio():
    draft = (
        "# Titel\n\n"
        "Ich schreibe den Bericht und schicke ihn ans Team. "
        "Am Morgen lese ich ihn erneut. Ich trinke einen Kaffee."
    )
    report = await readability_report(draft, language="de")
    assert report.passive_voice_ratio is not None
    assert report.passive_voice_ratio == 0.0


@pytest.mark.asyncio
async def test_readability_italian_uses_gulpease():
    draft = "# Titolo\n\nQuesto è un testo breve. Le frasi sono semplici. La lettura è facile."
    report = await readability_report(draft, language="it")
    assert report.formula_used == "gulpease-it"
    assert 0.0 <= report.score <= 100.0
    assert report.passive_voice_ratio is not None


@pytest.mark.asyncio
async def test_readability_italian_passive_detected():
    draft = (
        "# Titolo\n\n"
        "Il documento è stato firmato e il progetto è stato approvato dal team. "
        "I dati sono stati analizzati e il rapporto è stato inviato."
    )
    report = await readability_report(draft, language="it")
    assert report.passive_voice_ratio is not None
    assert report.passive_voice_ratio > 0


@pytest.mark.asyncio
async def test_readability_french_passive_detected():
    draft = (
        "# Titre\n\n"
        "Le rapport est signé par le directeur. "
        "Les données sont analysées et les résultats sont publiés."
    )
    report = await readability_report(draft, language="fr")
    assert report.passive_voice_ratio is not None
    assert report.passive_voice_ratio > 0


@pytest.mark.asyncio
async def test_readability_spanish_passive_detected():
    draft = (
        "# Título\n\n"
        "El informe es firmado por el director. "
        "Los datos son analizados y los resultados son publicados."
    )
    report = await readability_report(draft, language="es")
    assert report.passive_voice_ratio is not None
    assert report.passive_voice_ratio > 0


@pytest.mark.asyncio
async def test_readability_reading_time_english():
    # 238 words body + 1 title word = 239 total → ceil(239/238*60) = 61s
    words = " ".join(["word"] * 238)
    draft = f"# Title\n\n{words}"
    report = await readability_report(draft, language="en")
    assert report.reading_time_seconds == 61


@pytest.mark.asyncio
async def test_readability_reading_time_turkish():
    # 180 words body + 1 title word = 181 total → ceil(181/180*60) = 61s
    words = " ".join(["kelime"] * 180)
    draft = f"# Başlık\n\n{words}"
    report = await readability_report(draft, language="tr")
    assert report.reading_time_seconds == 61


@pytest.mark.asyncio
async def test_readability_reading_time_nonzero():
    draft = "# Title\n\nThis is a short sentence."
    report = await readability_report(draft, language="en")
    assert report.reading_time_seconds >= 1


@pytest.mark.asyncio
async def test_readability_french_uses_kandel_moles():
    draft = "# Titre\n\nVoici un texte court. Les phrases sont simples. La lecture est facile."
    report = await readability_report(draft, language="fr")
    assert report.formula_used == "kandel-moles-fr"
    assert 0.0 <= report.score
    assert report.passive_voice_ratio is not None


@pytest.mark.asyncio
async def test_readability_portuguese_uses_flesch_pt():
    draft = "# Título\n\nEste é um texto curto. As frases são simples. A leitura é fácil."
    report = await readability_report(draft, language="pt")
    assert report.formula_used == "flesch-pt"
    assert 0.0 <= report.score
    assert report.passive_voice_ratio is not None


@pytest.mark.asyncio
async def test_readability_portuguese_passive_detected():
    draft = (
        "# Título\n\n"
        "O relatório foi assinado pelo diretor. "
        "Os dados foram analisados e os resultados foram publicados."
    )
    report = await readability_report(draft, language="pt")
    assert report.passive_voice_ratio is not None
    assert report.passive_voice_ratio > 0
