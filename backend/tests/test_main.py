from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """
    Test bahwa endpoint health check merespon dengan benar.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Omnius API is running and warm."}


def test_analyze_unauthorized():
    """Memastikan /api/analyze menolak request tanpa API key."""
    response = client.post("/api/analyze", json={"articles": [], "model": "test"})
    assert response.status_code == 401


def test_research_unauthorized():
    """Memastikan /api/research menolak request tanpa API key."""
    response = client.post("/api/research", json={"topic": "test"})
    assert response.status_code == 401
