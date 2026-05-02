import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Tuple

from app.services.narrative_extractor import NarrativeExtractor
from app.services.scraper import scrape_article
from app.models.schemas import NewsAnalysisModel, AnalysisResultModel
from app.services.analyzer import generate_comparative_report # Kita masih gunakan fungsi ini untuk sementara

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
            # Simulasi langkah untuk setiap artikel
            source_info = getattr(provider, 'url', f"Artikel {i+1}")
            yield {"status": "progress", "message": f"Sedang mengambil konten: {source_info}", "percent": 10 + (i * 20)}
            
            res = self._process_single_article(provider)
            if res:
                results.append(res)
                yield {"status": "progress", "message": f"Analisis framing selesai: {res.source}", "percent": 25 + (i * 20)}
            else:
                yield {"status": "progress", "message": f"Peringatan: Gagal memproses {source_info}", "percent": 25 + (i * 20)}

        valid_analyses = [res for res in results if res is not None]
        
        if len(valid_analyses) < 2:
            yield {"status": "error", "message": "Minimal 2 artikel harus berhasil diproses."}
            return

        yield {"status": "progress", "message": "Menyusun laporan komparatif intelijen...", "percent": 90}
        
        comparative_report = generate_comparative_report(valid_analyses, self.model_name)

        final_result = AnalysisResultModel(
            analyses=valid_analyses,
            comparativeReport=comparative_report,
        )
        
        yield {"status": "final_result", "data": final_result.model_dump()}

    def _process_articles_parallel(self, providers: List[ArticleProvider]) -> List[NewsAnalysisModel | None]:
        with ThreadPoolExecutor(max_workers=min(len(providers), 5)) as executor:
            return list(executor.map(self._process_single_article, providers))

    def _process_single_article(self, provider: ArticleProvider) -> NewsAnalysisModel | None:
        """
        Logika pemrosesan satu unit artikel menggunakan provider.
        """
        try:
            title, text, error = provider.get_content()
            
            if error:
                logger.error(f"Gagal mendapatkan konten: {error}")
                return None

            if not text:
                return None

            # Kita asumsikan URL ada di provider jika tipenya URLArticleProvider
            url = getattr(provider, 'url', "")
            
            return self.extractor.extract(text, title=title, url=url)

        except Exception as e:
            logger.exception(f"Gagal memproses artikel: {str(e)}")
            return None
