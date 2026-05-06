import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Tuple

from app.services.narrative_extractor import NarrativeExtractor
from app.services.scraper import scrape_article
from app.models.schemas import NewsAnalysisModel, ComparativeReportModel, AnalysisResultModel
import json
from groq import Groq, APIError, RateLimitError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from app.core.config import COMPARATIVE_SYSTEM_PROMPT

from app.services.providers import ArticleProvider

logger = logging.getLogger(__name__)

class AnalysisPipeline:
    """
    Modul Orchestrator yang mengelola alur kerja analisis multi-artikel.
    Menangani paralelisme dan kebijakan kegagalan (Partial Success).
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.extractor = NarrativeExtractor(model_name)

    def run_stream(self, providers: List[ArticleProvider]):
        """
        Versi streaming dari pipeline yang mengirimkan progress secara real-time.
        """
        yield {"status": "progress", "message": f"Memulai analisis untuk {len(providers)} artikel...", "percent": 5}
        
        results = []
        for i, provider in enumerate(providers):
            # Inject temporary ID untuk auto-numbering jika judul kosong
            setattr(provider, 'temp_id', f"Berita {i+1}")
            
            source_info = getattr(provider, 'url', f"Artikel {i+1}")
            yield {"status": "progress", "message": f"Sedang menganalisis framing: {source_info}", "percent": 10 + (i * 20)}
            
            res, error_detail = self._process_single_article_with_error(provider)
            if res:
                results.append(res)
                yield {"status": "progress", "message": f"Berhasil dianalisis: {res.source}", "percent": 25 + (i * 20)}
            else:
                error_msg = f"Gagal memproses {source_info}: {error_detail}" if error_detail else f"Gagal memproses {source_info}"
                logger.error(f"PIPELINE ERROR [{source_info}]: {error_detail}")
                yield {"status": "progress", "message": f"Peringatan: {error_msg}", "percent": 25 + (i * 20)}

        valid_analyses = [res for res in results if res is not None]
        logger.info(f"Analisis selesai: {len(valid_analyses)} dari {len(providers)} artikel berhasil diproses.")
        
        if len(valid_analyses) < 2:
            error_msg = f"Minimal 2 artikel harus berhasil diproses. Hanya {len(valid_analyses)} yang berhasil."
            logger.error(error_msg)
            yield {"status": "error", "message": error_msg}
            return

        # 3. Generate Comparative Report
        yield {"status": "progress", "message": "Menyusun laporan komparatif intelijen...", "percent": 90}
        comparative_report = self._generate_comparative_report(valid_analyses)
        
        # 4. Final Result
        final_result = AnalysisResultModel(
            analyses=valid_analyses,
            comparativeReport=comparative_report
        )
        
        yield {"status": "final_result", "data": final_result.model_dump()}

    def _generate_comparative_report(self, analyses: list[NewsAnalysisModel]) -> ComparativeReportModel:
        """Membuat laporan komparatif antar media menggunakan Groq."""
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY tidak ditemukan.")
        
        client = Groq(api_key=api_key)
        
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
            model=self.model_name,
            messages=[
                {"role": "system", "content": COMPARATIVE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )

        data = json.loads(completion.choices[0].message.content)
        return ComparativeReportModel.model_validate(data)

    def _process_articles_parallel(self, providers: List[ArticleProvider]) -> List[NewsAnalysisModel | None]:
        with ThreadPoolExecutor(max_workers=min(len(providers), 5)) as executor:
            return list(executor.map(self._process_single_article, providers))

    def _process_single_article(self, provider: ArticleProvider) -> NewsAnalysisModel | None:
        """
        Versi wrapper untuk kompatibilitas ke belakang.
        """
        res, _ = self._process_single_article_with_error(provider)
        return res

    def _process_single_article_with_error(self, provider: ArticleProvider) -> Tuple[NewsAnalysisModel | None, str | None]:
        """
        Logika pemrosesan satu unit artikel menggunakan provider.
        Mengembalikan tuple: (Hasil Analisis, Pesan Error jika gagal)
        """
        try:
            title, text, error = provider.get_content()
            
            if error:
                logger.error(f"Gagal mendapatkan konten: {error}")
                return None, str(error)

            if not text:
                return None, "Teks berita kosong."

            # Auto-numbering jika judul kosong
            final_title = title or getattr(provider, 'temp_id', "Berita")
            
            # Kita asumsikan URL ada di provider jika tipenya URLArticleProvider
            url = getattr(provider, 'url', "")
            
            result = self.extractor.extract(text, title=final_title, url=url)
            return result, None

        except Exception as e:
            error_msg = str(e)
            logger.exception(f"Gagal memproses artikel: {error_msg}")
            # Jika ini adalah RetryError dari tenacity, ambil pesan aslinya jika mungkin
            return None, error_msg
