import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

# ── API Key Setup ─────────────────────────────────────────────────────────────
# Set environment variable for testing
@pytest.fixture(autouse=True)
def setup_api_key(monkeypatch):
    monkeypatch.setenv("OMNIUS_API_KEY", "test-key")

def auth_headers():
    return {"X-API-Key": "test-key"}

# ── TDD Cycle 4: Analyze Validation ───────────────────────────────────────────

def test_analyze_validation_min_articles():
    """Memastikan /api/analyze menolak jika artikel < 2."""
    payload = {
        "articles": [{"url": "https://test.com"}],
        "model": "llama-3.3-70b-versatile"
    }
    response = client.post("/api/analyze", json=payload, headers=auth_headers())
    assert response.status_code == 400
    assert "Minimal 2 artikel" in response.json()["detail"]

def test_analyze_validation_invalid_model():
    """Memastikan /api/analyze menolak jika model tidak tersedia."""
    payload = {
        "articles": [
            {"url": "https://test1.com"},
            {"url": "https://test2.com"}
        ],
        "model": "invalid-model"
    }
    response = client.post("/api/analyze", json=payload, headers=auth_headers())
    assert response.status_code == 400
    assert "tidak tersedia" in response.json()["detail"]


# ── TDD Cycle 5: Analyze Success Path ─────────────────────────────────────────

def test_analyze_success_stream():
    """Memastikan /api/analyze mengalirkan data dengan benar saat sukses."""
    mock_pipeline = MagicMock()
    
    def mock_run_stream(providers):
        yield {"status": "progress", "message": "Analisis dimulai", "percent": 10}
        yield {"status": "final_result", "data": {"analyses": [], "comparativeReport": {}}}

    mock_pipeline.run_stream.side_effect = mock_run_stream

    payload = {
        "articles": [
            {"url": "https://test1.com"},
            {"url": "https://test2.com"}
        ],
        "model": "llama-3.3-70b-versatile"
    }

    # Gunakan TestClient with streaming
    with patch("app.main.AnalysisPipeline", return_value=mock_pipeline):
        with client.stream("POST", "/api/analyze", json=payload, headers=auth_headers()) as response:
            assert response.status_code == 200
            
            lines = list(response.iter_lines())
            # Cari baris data:
            data_lines = [line for line in lines if line.startswith("data: ")]
            assert len(data_lines) == 2
            
            import json
            first_event = json.loads(data_lines[0].replace("data: ", ""))
            assert first_event["status"] == "progress"
            
            last_event = json.loads(data_lines[1].replace("data: ", ""))
            assert last_event["status"] == "final_result"


# ── TDD Cycle 6: Research Success Path ────────────────────────────────────────

@pytest.mark.asyncio
async def test_research_success():
    """Memastikan /api/research mengembalikan hasil riset saat sukses."""
    from app.models.schemas import ResearchResponse, ResearchArticleSchema
    
    mock_data = ResearchResponse(
        articles=[
            ResearchArticleSchema(
                title="News 1", 
                source="Source 1", 
                url="http://s1.com", 
                snippet="Snippet 1", 
                reason="Reason 1", 
                publishedDate="2026-05-04"
            )
        ]
    )

    with patch("app.main.research_news_by_topic", return_value=mock_data):
        response = client.post("/api/research", json={"topic": "AI"}, headers=auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert len(data["articles"]) == 1
        assert data["articles"][0]["title"] == "News 1"

def test_research_failure():
    """Memastikan /api/research menangani error internal dengan baik."""
    with patch("app.main.research_news_by_topic", side_effect=Exception("Research failed")):
        response = client.post("/api/research", json={"topic": "AI"}, headers=auth_headers())
        assert response.status_code == 500
        assert "Gagal melakukan riset" in response.json()["detail"]
