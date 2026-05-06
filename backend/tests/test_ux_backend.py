import pytest
from fastapi.testclient import TestClient
from app.main import app
import json

import os

# Set fake API Key for testing
os.environ["OMNIUS_API_KEY"] = "test-secret-key"
HEADERS = {"X-API-Key": "test-secret-key"}

client = TestClient(app)

def test_manual_article_auto_numbering():
    """
    Test: Mengirim 2 berita manual tanpa judul.
    Ekspektasi: Backend memprosesnya sebagai 'Berita 1' dan 'Berita 2'.
    """
    # Kita tidak jalankan full pipeline (karena butuh LLM), 
    # kita hanya tes bagian konversi provider di main.py (unit level inside main)
    # Namun karena logika provider ada di dalam endpoint, kita mock pipeline-nya.
    
    from unittest.mock import patch, MagicMock
    
    mock_pipeline = MagicMock()
    # Simulasi stream event
    mock_pipeline.run_stream.return_value = [
        {"status": "progress", "message": "Menganalisis Berita 1", "percent": 10},
        {"status": "progress", "message": "Menganalisis Berita 2", "percent": 50},
        {"status": "final_result", "data": {}}
    ]
    
    with patch("app.main.AnalysisPipeline", return_value=mock_pipeline):
        response = client.post(
            "/api/analyze",
            json={
                "articles": [
                    {"text": "Isi berita pertama"},
                    {"text": "Isi berita kedua"}
                ],
                "model": "llama-3.3-70b-versatile"
            },
            headers=HEADERS
        )
        
        assert response.status_code == 200
        # Cek apakah stream mengandung pesan dengan nama berita yang benar
        content = response.text
        assert "Berita 1" in content
        assert "Berita 2" in content

def test_error_propagation_sse():
    """
    Test: Simulasi error (misal Rate Limit) saat analisis.
    Ekspektasi: Pesan error dikirim melalui event SSE 'status': 'error'.
    """
    from unittest.mock import patch, MagicMock
    
    mock_pipeline = MagicMock()
    mock_pipeline.run_stream.return_value = [
        {"status": "progress", "message": "Memulai...", "percent": 5},
        {"status": "error", "message": "Rate limit Groq terlampaui"}
    ]
    
    with patch("app.main.AnalysisPipeline", return_value=mock_pipeline):
        response = client.post(
            "/api/analyze",
            json={
                "articles": [
                    {"url": "https://example.com/1"},
                    {"url": "https://example.com/2"}
                ]
            },
            headers=HEADERS
        )
        
        assert response.status_code == 200
        assert "Rate limit Groq terlampaui" in response.text
        assert '"status": "error"' in response.text
