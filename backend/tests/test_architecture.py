import pytest
import json
from unittest.mock import MagicMock, patch
from app.services.narrative_extractor import NarrativeExtractor
from app.services.providers import ManualArticleProvider
from app.services.pipeline import AnalysisPipeline
from app.models.schemas import NewsAnalysisModel

def test_narrative_extractor_behavior():
    """
    Verifikasi bahwa NarrativeExtractor (Deep Module) dapat mengelola 
    ekstraksi framing dengan benar.
    """
    # Mock os.environ agar tidak ValueError
    with patch.dict('os.environ', {'GROQ_API_KEY': 'fake-key'}):
        # Mock Groq Client
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = json.dumps({
            "summary": "Test Summary",
            "framing": {
                "problemDefinition": "Prob",
                "causalInterpretation": "Cause",
                "moralEvaluation": "Moral",
                "treatmentRecommendation": "Treat"
            },
            "actors": [],
            "keywords": ["test"],
            "overallSentiment": 0.0
        })
        mock_client.chat.completions.create.return_value = mock_completion

        with patch('app.services.narrative_extractor.Groq', return_value=mock_client):
            extractor = NarrativeExtractor(model_name="test-model")
            result = extractor.extract("Teks berita palsu", title="Judul", url="https://test.com")
            
            assert isinstance(result, NewsAnalysisModel)
            assert result.title == "Judul"
            assert result.source == "test.com"

def test_article_provider_manual():
    """
    Verifikasi bahwa ManualArticleProvider (Adapter) bekerja sesuai kontrak.
    """
    provider = ManualArticleProvider(title="Manual", text="Isi berita manual")
    title, text, error = provider.get_content()
    
    assert title == "Manual"
    assert text == "Isi berita manual"
    assert error is None

@pytest.mark.asyncio
async def test_pipeline_streaming_logic():
    """
    Verifikasi bahwa AnalysisPipeline memancarkan event progress yang benar.
    """
    from app.models.schemas import ComparativeReportModel
    
    mock_extractor = MagicMock()
    mock_extractor.extract.return_value = NewsAnalysisModel(
        title="T", source="S", summary="Sum", 
        framing={"problemDefinition": "P", "causalInterpretation": "C", "moralEvaluation": "M", "treatmentRecommendation": "R"},
        actors=[], keywords=[], overallSentiment=0.0
    )

    with patch.dict('os.environ', {'GROQ_API_KEY': 'fake-key'}):
        with patch('app.services.pipeline.NarrativeExtractor', return_value=mock_extractor):
            with patch('app.services.pipeline.AnalysisPipeline._generate_comparative_report') as mock_comp:
                # Berikan model Pydantic yang valid agar tidak ValidationError
                mock_comp.return_value = ComparativeReportModel(
                    summary="Laporan Komparatif",
                    keyDifferences=["Diff 1"],
                    sharedNarratives=["Shared 1"],
                    biasIndicator="None"
                )
                
                pipeline = AnalysisPipeline(model_name="test")
                providers = [
                    ManualArticleProvider(title="A1", text="T1"),
                    ManualArticleProvider(title="A2", text="T2")
                ]
                
                events = []
                async for event in pipeline.run_stream(providers):
                    events.append(event)
                
                status_types = [e["status"] for e in events]
                assert "progress" in status_types
                assert "final_result" in status_types
