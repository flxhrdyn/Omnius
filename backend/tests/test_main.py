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

def test_cors_unauthorized():
    """
    Test bahwa origin yang tidak diizinkan tidak mendapatkan header CORS yang benar.
    """
    # Catatan: TestClient menggunakan instance app yang sudah dimuat.
    # Jika defaultnya adalah "*", maka semua origin akan di-echo kembali oleh Starlette
    # KECUALI jika kita menguji perilaku dengan env var tertentu.
    response = client.options(
        "/api/health",
        headers={
            "Origin": "https://malicious-site.com",
            "Access-Control-Request-Method": "GET"
        }
    )
    # Jika "*" ada di allowed_origins, Starlette akan mengembalikan Access-Control-Allow-Origin: https://malicious-site.com
    # karena kita set allow_credentials=True.
    # Verifikasi bahwa request ditolak dengan status 400 (Bad Request) oleh Starlette
    assert response.status_code == 400
