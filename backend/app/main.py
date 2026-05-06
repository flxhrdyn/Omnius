"""
FastAPI Backend for News Framing Analysis
Menyediakan API endpoint yang menghubungkan React frontend
dengan logika scraping dan analisis Groq di Python.
"""

import os
import json
import logging
import asyncio
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, HTTPException, Request, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

# Konfigurasi Logging agar muncul di terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Muat environment variables dengan lebih reliabel
load_dotenv(find_dotenv())

from app.services.pipeline import AnalysisPipeline
from app.services.agent_service import research_news_by_topic
from app.core.config import AVAILABLE_MODELS
from app.models.schemas import ResearchRequest, ResearchResponse

app = FastAPI(
    title="Omnius AI API",
    description="Backend API untuk analisis framing berita menggunakan Groq dan Pydantic AI.",
    version="1.0.0",
)

# ── CORS Configuration ───────────────────────────────────────────────────────
# Baca dari env; fallback ke localhost port 5173 dan 3000 untuk keamanan.
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

# Pastikan port development masuk dalam daftar
for origin in ["http://localhost:5173", "http://localhost:3000"]:
    if origin not in allowed_origins:
        allowed_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Key Security ────────────────────────────────────────────────────────
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    master_key = os.getenv("OMNIUS_API_KEY")
    if not master_key:
        logger.warning("OMNIUS_API_KEY tidak dikonfigurasi di backend!")
        return None
    if api_key != master_key:
        raise HTTPException(status_code=403, detail="Akses ditolak: API Key tidak valid.")
    return api_key

# ── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Omnius API is running and warm."}

@app.get("/api/models")
async def get_models():
    return {"models": AVAILABLE_MODELS}

@app.post("/api/research")
async def research_endpoint(request: ResearchRequest, api_key: str = Depends(get_api_key)):
    """
    Endpoint SSE untuk mencari berita berdasarkan topik dengan progress real-time.
    """
    async def event_generator():
        try:
            # Queue untuk menangkap progress dari agent
            queue = asyncio.Queue()

            def on_progress(msg: str):
                queue.put_nowait(msg)

            # Jalankan riset di background task
            task = asyncio.create_task(research_news_by_topic(request.topic, on_progress=on_progress))

            while not task.done() or not queue.empty():
                try:
                    # Ambil pesan dari queue dengan timeout singkat agar bisa memberikan heartbeat
                    msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {json.dumps({'status': 'progress', 'message': msg})}\n\n"
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"

            # Ambil hasil akhir
            result = await task
            # Konversi hasil ke skema response agar konsisten dengan frontend
            from app.models.schemas import ResearchArticleSchema
            articles_data = [
                ResearchArticleSchema(
                    title=a.title,
                    source=a.source,
                    url=a.url,
                    snippet=a.snippet,
                    reason=a.reason,
                    publishedDate=a.published_date,
                    relevanceScore=a.relevance_score
                ).model_dump() for a in result.articles
            ]
            
            # DIAGNOSTIC LOG
            logger.info(f"SSE sending final_result: {len(articles_data)} articles, isFallback: {result.is_fallback}")
            
            # Kirim flag isFallback ke frontend menggunakan status 'final_result' sesuai apiService.ts
            yield f"data: {json.dumps({'status': 'final_result', 'data': {'articles': articles_data, 'isFallback': result.is_fallback}})}\n\n"

        except Exception as e:
            logger.exception("Gagal dalam proses riset")
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/analyze")
async def analyze_news(request: Request, api_key: str = Depends(get_api_key)):
    """
    Menerima list URL atau Teks Manual dan menjalankan pipeline analisis framing.
    """
    data = await request.json()
    items = data.get("items", [])
    model_name = data.get("model", "llama-3.3-70b-versatile")
    
    if not items:
        raise HTTPException(status_code=400, detail="Daftar artikel tidak boleh kosong.")

    from app.services.providers import URLArticleProvider, ManualArticleProvider

    providers = []
    for item in items:
        if item.get("type") == "url":
            providers.append(URLArticleProvider(item["url"]))
        elif item.get("type") == "manual":
            providers.append(ManualArticleProvider(title=item.get("title"), text=item["text"]))

    pipeline = AnalysisPipeline(model_name=model_name)
    
    async def event_generator():
        try:
            it = pipeline.run_stream(providers).__aiter__()
            while True:
                try:
                    event = await asyncio.wait_for(it.__anext__(), timeout=15.0)
                    yield f"data: {json.dumps(event)}\n\n"
                except StopAsyncIteration:
                    break
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
        except Exception as e:
            logger.exception("Pipeline Error")
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
