"""
News Framing Analyzer
Modul ini bertanggung jawab untuk menganalisis teks berita menggunakan Groq.
Dipisahkan dari Streamlit agar bisa digunakan oleh FastAPI backend.
"""

import os
import json
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple

from groq import Groq, APIError, RateLimitError
from langdetect import detect, LangDetectException
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from app.core.config import (
    FRAMING_SYSTEM_PROMPT,
    COMPARATIVE_SYSTEM_PROMPT,
)
from app.services.scraper import scrape_article
from app.models.schemas import NewsAnalysisModel, ComparativeReportModel, AnalysisResultModel


# Struktur data yang menyimpan semua informasi hasil analisis untuk satu artikel.
ArticleAnalysis = namedtuple(
    "ArticleAnalysis",
    ["url", "title", "text", "analysis_results", "error", "lang"],
)


def _get_groq_client() -> Groq:
    """Membuat instance Groq client menggunakan API key dari environment variable.

    API key diambil dari environment variable GROQ_API_KEY.
    Kompatibel dengan file .env dan deployment apapun tanpa Streamlit.

    Returns:
        Instance Groq client.

    Raises:
        ValueError: Jika API key tidak ditemukan.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY tidak ditemukan di environment variables.")
    return Groq(api_key=api_key)


@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((APIError, RateLimitError))
)
def analyze_article_text(article_text: str, model_name: str, title: str = "", url: str = "") -> NewsAnalysisModel:
    """Menganalisis satu artikel berita menggunakan model AI Groq.

    Menghasilkan objek NewsAnalysisModel yang kompatibel dengan React frontend.

    Args:
        article_text: Teks bersih dari artikel yang akan dianalisis.
        model_name: Nama model Groq yang akan digunakan.
        title: Judul artikel (opsional, untuk dimasukkan ke hasil).
        url: URL artikel (opsional, untuk mengekstrak nama sumber).

    Returns:
        Objek NewsAnalysisModel.

    Raises:
        Exception: Jika Groq API gagal atau JSON tidak valid.
    """
    client = _get_groq_client()

    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": FRAMING_SYSTEM_PROMPT},
            {"role": "user", "content": article_text},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    raw_json = completion.choices[0].message.content
    data = json.loads(raw_json)

    # Ekstrak nama sumber dari URL jika tidak ada di response
    source = url.split("/")[2].replace("www.", "") if url and "/" in url else url or "Sumber Tidak Diketahui"

    # Gabungkan title dan source ke dalam data jika belum ada
    if "title" not in data or not data["title"]:
        data["title"] = title or "Judul Tidak Tersedia"
    if "source" not in data or not data["source"]:
        data["source"] = source

    return NewsAnalysisModel.model_validate(data)


@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((APIError, RateLimitError))
)
def generate_comparative_report(analyses: list[NewsAnalysisModel], model_name: str) -> ComparativeReportModel:
    """Membuat laporan analisis komparatif dari beberapa hasil analisis artikel.

    Args:
        analyses: List objek NewsAnalysisModel dari beberapa artikel.
        model_name: Nama model Groq yang akan digunakan.

    Returns:
        Objek ComparativeReportModel.

    Raises:
        Exception: Jika Groq API gagal atau JSON tidak valid.
    """
    client = _get_groq_client()

    context_parts = []
    for analysis in analyses:
        framing_text = (
            f"Problem Definition: {analysis.framing.problemDefinition}\n"
            f"Causal Interpretation: {analysis.framing.causalInterpretation}\n"
            f"Moral Evaluation: {analysis.framing.moralEvaluation}\n"
            f"Treatment Recommendation: {analysis.framing.treatmentRecommendation}"
        )
        context_parts.append(f"Sumber: {analysis.source} ({analysis.title})\n{framing_text}")

    context = "\n\n---\n\n".join(context_parts)
    user_prompt = f"Buatlah laporan analisis komparatif berdasarkan data framing berikut:\n\n{context}"

    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": COMPARATIVE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )

    raw_json = completion.choices[0].message.content
    data = json.loads(raw_json)
    return ComparativeReportModel.model_validate(data)


def run_full_analysis(
    articles: list[dict],
    model_name: str,
) -> AnalysisResultModel:
    """Menjalankan pipeline analisis lengkap: scraping, analisis per artikel, dan laporan komparatif.

    Args:
        articles: List dict dengan key 'url' atau key 'title' + 'text'.
        model_name: Nama model Groq yang digunakan.

    Returns:
        Objek AnalysisResultModel yang siap dikirimkan ke React frontend.

    Raises:
        ValueError: Jika artikel yang berhasil dianalisis kurang dari 2.
    """
    def _process_one(article: dict) -> tuple[NewsAnalysisModel | None, str | None]:
        """Memproses satu artikel: scraping (jika URL) lalu analisis."""
        try:
            if "url" in article and article["url"]:
                url = article["url"]
                title, text, error = scrape_article(url)
                if error:
                    return None, f"Gagal scraping {url}: {error}"
            else:
                url = ""
                title = article.get("title", "")
                text = article.get("text", "")

            if not text:
                return None, "Teks artikel kosong."

            result = analyze_article_text(text, model_name, title=title, url=url)
            return result, None

        except Exception as e:
            return None, str(e)

    # Proses semua artikel secara paralel
    with ThreadPoolExecutor(max_workers=len(articles)) as executor:
        outcomes = list(executor.map(_process_one, articles))

    errors = [err for _, err in outcomes if err]
    valid_analyses = [res for res, _ in outcomes if res is not None]

    if errors:
        error_detail = "; ".join(errors)
        raise ValueError(f"Gagal memproses beberapa artikel: {error_detail}")

    if len(valid_analyses) < 2:
        raise ValueError("Minimal 2 artikel harus diberikan untuk analisis komparatif.")

    comparative = generate_comparative_report(valid_analyses, model_name)

    return AnalysisResultModel(
        analyses=valid_analyses,
        comparativeReport=comparative,
    )
