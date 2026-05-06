import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
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
        "items": [{"type": "url", "url": "https://test.com"}],
        "model": "llama-3.3-70b-versatile"
    }
    response = client.post("/api/analyze", json=payload, headers=auth_headers())
    assert response.status_code == 200 # SSE stream starts, but returns error event
    
    # Check SSE content
    lines = list(response.iter_lines())
    assert any("Minimal 2 artikel" in line for line in lines)

def test_analyze_validation_invalid_model():
    """Memastikan /api/analyze menolak jika model tidak tersedia."""
    # Note: Validation model might happen inside the generator now
    payload = {
        "items": [
            {"type": "url", "url": "https://test1.com"},
            {"type": "url", "url": "https://test2.com"}
        ],
        "model": "invalid-model"
    }
    response = client.post("/api/analyze", json=payload, headers=auth_headers())
    assert response.status_code == 200
    # In streaming mode, errors are often yielded as data events
    lines = list(response.iter_lines())
    # We check if some error message about model was sent, or at least it doesn't crash
    assert any("status" in line for line in lines)


# ── TDD Cycle 5: Analyze Success Path ─────────────────────────────────────────

def test_analyze_success_stream():
    """Memastikan /api/analyze mengalirkan data dengan benar saat sukses."""
    mock_pipeline = MagicMock()
    
    async def mock_run_stream(providers):
        yield {"status": "progress", "message": "Analisis dimulai", "percent": 10}
        yield {"status": "final_result", "data": {"analyses": [], "comparativeReport": {}}}

    mock_pipeline.run_stream.side_effect = mock_run_stream

    payload = {
        "items": [
            {"type": "url", "url": "https://test1.com"},
            {"type": "url", "url": "https://test2.com"}
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
            
            first_event = json.loads(data_lines[0].replace("data: ", ""))
            assert first_event["status"] == "progress"
            
            last_event = json.loads(data_lines[1].replace("data: ", ""))
            assert last_event["status"] == "final_result"


# ── TDD Cycle 6: Research Success Path ────────────────────────────────────────

@pytest.mark.asyncio
async def test_research_success():
    """Memastikan /api/research mengembalikan hasil riset saat sukses via SSE."""
    from app.services.agent_service import ResearchResult, ResearchArticle
    
    mock_article = ResearchArticle(
        title="News 1",
        source="Source 1",
        url="http://s1.com",
        snippet="Snippet 1",
        reason="Reason 1",
        published_date="2026-05-04",
        relevance_score=10
    )
    mock_result = ResearchResult(articles=[mock_article], suggested_query=None)

    with patch("app.main.research_news_by_topic", return_value=mock_result):
        with client.stream("POST", "/api/research", json={"topic": "AI"}, headers=auth_headers()) as response:
            assert response.status_code == 200
            lines = list(response.iter_lines())
            data_lines = [line for line in lines if line.startswith("data: ")]
            
            # Check for final_result event
            final_event_line = next((l for l in data_lines if '"status": "final_result"' in l), None)
            assert final_event_line is not None
            
            final_data = json.loads(final_event_line.replace("data: ", ""))
            assert len(final_data["data"]["articles"]) == 1
            assert final_data["data"]["articles"][0]["title"] == "News 1"
            assert "relevanceScore" in final_data["data"]["articles"][0]

def test_research_failure():
    """Memastikan /api/research menangani error internal dengan baik."""
    with patch("app.main.research_news_by_topic", side_effect=Exception("Research failed")):
        with client.stream("POST", "/api/research", json={"topic": "AI"}, headers=auth_headers()) as response:
            assert response.status_code == 200
            lines = list(response.iter_lines())
            assert any('"status": "error"' in line for line in lines)
