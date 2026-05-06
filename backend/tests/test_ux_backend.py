from app.services.providers import ManualArticleProvider

def test_manual_article_provider_fallback_title():
    """
    Memastikan ManualArticleProvider menggunakan fallback_title jika title kosong.
    """
    # Case 1: Title kosong, gunakan fallback
    provider1 = ManualArticleProvider(title="", text="Isi berita 1", fallback_title="Berita 1")
    title1, _, _ = provider1.get_content()
    assert title1 == "Berita 1"

    # Case 2: Title ada, gunakan title asli
    provider2 = ManualArticleProvider(title="Judul Asli", text="Isi berita 2", fallback_title="Berita 2")
    title2, _, _ = provider2.get_content()
    assert title2 == "Judul Asli"

def test_manual_article_provider_default_fallback():
    """
    Memastikan fallback default tetap bekerja jika tidak dipassing.
    """
    provider = ManualArticleProvider(title="", text="Isi berita")
    title, _, _ = provider.get_content()
    assert title == "Judul Manual"

# --- Integration Tests ---
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_api_key(monkeypatch):
    monkeypatch.setenv("OMNIUS_API_KEY", "test-key")

def auth_headers():
    return {"X-API-Key": "test-key"}

def test_analyze_manual_numbering_integration():
    """
    Memastikan endpoint /api/analyze memberikan nomor pada berita manual tanpa judul.
    """
    mock_pipeline = MagicMock()
    captured_providers = []

    def mock_run_stream(providers):
        nonlocal captured_providers
        captured_providers = providers
        yield {"status": "progress", "message": "Analisis dimulai", "percent": 10}
        yield {"status": "final_result", "data": {"analyses": [], "comparativeReport": {}}}

    mock_pipeline.run_stream.side_effect = mock_run_stream

    payload = {
        "articles": [
            {"text": "Isi berita manual 1"}, # No title
            {"title": "Judul Custom", "text": "Isi berita manual 2"}, # With title
            {"text": "Isi berita manual 3"} # No title
        ],
        "model": "llama-3.3-70b-versatile"
    }

    with patch("app.main.AnalysisPipeline", return_value=mock_pipeline):
        with client.stream("POST", "/api/analyze", json=payload, headers=auth_headers()) as response:
            assert response.status_code == 200
            
            # Verifikasi provider yang diterima pipeline
            assert len(captured_providers) == 3
            
            # Berita 1 (Manual 1)
            t1, _, _ = captured_providers[0].get_content()
            assert t1 == "Berita 1"
            
            # Berita 2 (Judul Custom)
            t2, _, _ = captured_providers[1].get_content()
            assert t2 == "Judul Custom"
            
            # Berita 3 (Manual 2 tanpa judul -> Berita 3)
            t3, _, _ = captured_providers[2].get_content()
            assert t3 == "Berita 3"
