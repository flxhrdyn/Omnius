from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """
    Test bahwa endpoint health check merespon dengan benar.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Omnius API is running."}

# Kita hapus test_cors_unauthorized karena saat ini kita menggunakan kebijakan 
# allowed_origins=["*"] yang mengizinkan semua akses demi kemudahan deployment.
