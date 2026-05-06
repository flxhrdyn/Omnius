import os
os.environ["GROQ_API_KEY"] = "dummy_key"

import pytest
from app.services.providers import ManualArticleProvider
from app.services.pipeline import AnalysisPipeline
from app.services.narrative_extractor import NarrativeExtractor
from app.models.schemas import NewsAnalysisModel, ComparativeReportModel, FramingModel
from unittest.mock import MagicMock, patch

@pytest.mark.asyncio
async def test_manual_articles_get_auto_numbered():
    """
    Tes untuk memastikan artikel manual tanpa judul otomatis diberi nomor.
    """
    # Buat dummy model sesuai skema terbaru
    dummy_framing = FramingModel(
        problemDefinition="...",
        causalInterpretation="...",
        moralEvaluation="...",
        treatmentRecommendation="..."
    )
    dummy_analysis = NewsAnalysisModel(
        title="Title",
        source="Source",
        url="https://test.com",
        summary="Summary text",
        framing=dummy_framing,
        actors=[],
        keywords=["k1", "k2"],
        overallSentiment=0.5
    )
    dummy_report = ComparativeReportModel(
        summary="Executive summary comparison",
        keyDifferences=["diff1"],
        sharedNarratives=["same1"],
        biasIndicator="Low bias"
    )

    # Buat provider tanpa judul
    p1 = ManualArticleProvider(title="", text="Isi berita 1")
    p2 = ManualArticleProvider(title="Judul Kustom", text="Isi berita 2")
    p3 = ManualArticleProvider(title=None, text="Isi berita 3")
    
    pipeline = AnalysisPipeline(model_name="llama-3.1-8b-instant")
    
    # Patch NarrativeExtractor.extract
    with patch.object(NarrativeExtractor, "extract") as mock_extract:
        mock_extract.return_value = dummy_analysis
        
        # Patch _generate_comparative_report
        with patch.object(AnalysisPipeline, "_generate_comparative_report") as mock_report:
            mock_report.return_value = dummy_report
            
            # Jalankan stream (yang akan memicu numbering)
            for event in pipeline.run_stream([p1, p2, p3]):
                pass
                
            # Periksa argumen yang dikirim ke extract
            calls = mock_extract.call_args_list
            
            # p1: title="" -> Berita 1
            assert calls[0].kwargs['title'] == "Berita 1"
            
            # p2: title="Judul Kustom" -> Judul Kustom
            assert calls[1].kwargs['title'] == "Judul Kustom"
            
            # p3: title=None -> Berita 3
            assert calls[2].kwargs['title'] == "Berita 3"
