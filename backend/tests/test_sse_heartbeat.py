import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_analyze_sse_heartbeat():
    """
    Memastikan bahwa endpoint /api/analyze mengirimkan heartbeat (: keep-alive)
    jika pipeline sedang lambat.
    """
    mock_pipeline = MagicMock()
    
    async def slow_generator(providers):
        # Kirim satu event awal
        yield {"status": "progress", "message": "Starting...", "percent": 0}
        # Simulasi delay agar heartbeat terpicu
        await asyncio.sleep(0.5) 
        yield {"status": "final_result", "data": {}}

    mock_pipeline.run_stream.side_effect = slow_generator

    request_data = {
        "items": [
            {"type": "url", "url": "https://test1.com"},
            {"type": "url", "url": "https://test2.com"}
        ],
        "model": "llama-3.3-70b-versatile"
    }

    from httpx import AsyncClient, ASGITransport

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        with patch.dict('os.environ', {'OMNIUS_API_KEY': 'test-key'}):
            with patch('app.main.AnalysisPipeline', return_value=mock_pipeline):
                # Kita patch asyncio.wait_for agar timeout-nya sangat kecil (0.1s)
                # sehingga heartbeat terpicu cepat dalam test.
                original_wait_for = asyncio.wait_for

                async def mock_wait_for(aw, timeout):
                    # Jika timeout 15.0 (nilai produksi), gunakan 0.1 untuk test
                    test_timeout = 0.1 if timeout == 15.0 else timeout
                    return await original_wait_for(aw, timeout=test_timeout)

                headers = {"X-API-Key": "test-key"}
                
                with patch('asyncio.wait_for', side_effect=mock_wait_for):
                    async with ac.stream("POST", "/api/analyze", json=request_data, headers=headers) as response:
                        assert response.status_code == 200
                        
                        heartbeat_received = False
                        async for line in response.aiter_lines():
                            if line == ": keep-alive":
                                heartbeat_received = True
                                break
                        
                        assert heartbeat_received, "Harus menerima heartbeat ': keep-alive'"
