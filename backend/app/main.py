"""
FastAPI Backend for News Framing Analysis
Menyediakan API endpoint yang menghubungkan React frontend
dengan logika scraping dan analisis Groq di Python.
"""

import os
import json
import logging
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, HTTPException, Request, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
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
# Baca dari env; fallback ke localhost saja (bukan wildcard) untuk keamanan.
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
# Selalu sertakan localhost untuk development
if "http://localhost:5173" not in allowed_origins:
    allowed_origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ── API Key Protection ────────────────────────────────────────────────────────
API_KEY_NAME = "X-API-Key"
_api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(api_key: str = Security(_api_key_header)):
    """Dependency: memastikan setiap request ke endpoint sensitif menyertakan API key yang valid."""
    expected_key = os.getenv("OMNIUS_API_KEY")
    # Jika OMNIUS_API_KEY tidak dikonfigurasi di environment, lewati pengecekan
    # (berguna saat development lokal tanpa .env)
    if not expected_key:
        logger.warning("OMNIUS_API_KEY tidak dikonfigurasi. Endpoint tidak terproteksi!")
        return
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="API key tidak valid atau tidak ditemukan.")

class ArticleInput(BaseModel):
    """Input untuk satu artikel: bisa berupa URL atau teks manual."""
    url: Optional[str] = None
    title: Optional[str] = None
    text: Optional[str] = None


class AnalyzeRequest(BaseModel):
    """Request body untuk endpoint analisis."""
    articles: list[ArticleInput]
    model: str = "llama-3.3-70b-versatile"


@app.get("/api/health")
def health_check():
    """Endpoint untuk mengecek apakah server berjalan dan melakukan pre-warming."""
    logger.info("Health check ping received - App is warm.")
    return {"status": "ok", "message": "Omnius API is running and warm."}


@app.get("/api/models")
def get_models():
    """Mengembalikan daftar model Groq yang tersedia."""
    return {"models": AVAILABLE_MODELS}


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest, _: None = Depends(verify_api_key)):
    """Endpoint utama: menerima URL atau teks, mengembalikan hasil analisis framing.

    Body JSON yang diharapkan:
    {
        "articles": [
            {"url": "https://..."},
            {"title": "Judul", "text": "Isi berita..."}
        ],
        "model": "llama-3.3-70b-versatile"
    }
    """
    if len(request.articles) < 2:
        raise HTTPException(status_code=400, detail="Minimal 2 artikel harus diberikan untuk analisis komparatif.")

    if request.model not in AVAILABLE_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{request.model}' tidak tersedia. Pilih dari: {AVAILABLE_MODELS}",
        )

    articles_data = [article.model_dump(exclude_none=True) for article in request.articles]

    # Langkah 3: Konversi data mentah menjadi ArticleProviders (Seam & Adapter)
    from app.services.providers import URLArticleProvider, ManualArticleProvider
    providers = []
    manual_count = 0
    for art in articles_data:
        if art.get("url"):
            providers.append(URLArticleProvider(art["url"]))
        else:
            manual_count += 1
            fallback = f"Berita {manual_count}"
            providers.append(ManualArticleProvider(art.get("title", ""), art.get("text", ""), fallback_title=fallback))

    try:
        pipeline = AnalysisPipeline(request.model)
        
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        async def event_generator():
            # Kita gunakan queue untuk menjembatani pipeline (sync) dengan generator (async)
            queue = asyncio.Queue()
            loop = asyncio.get_event_loop()
            
            def producer():
                try:
                    for event in pipeline.run_stream(providers):
                        loop.call_soon_threadsafe(queue.put_nowait, event)
                except Exception as e:
                    logger.error(f"Error in pipeline producer: {e}")
                    loop.call_soon_threadsafe(queue.put_nowait, {"status": "error", "message": str(e)})
                finally:
                    loop.call_soon_threadsafe(queue.put_nowait, None) # Sentinel

            # Jalankan pipeline di thread terpisah agar tidak memblock event loop
            executor = ThreadPoolExecutor(max_workers=1)
            loop.run_in_executor(executor, producer)

            while True:
                try:
                    # Tunggu event dengan timeout 15 detik untuk heartbeat
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                    if event is None:
                        break
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                except asyncio.TimeoutError:
                    # Kirim SSE comment sebagai heartbeat untuk mencegah Azure Load Balancer timeout
                    yield ": keep-alive\n\n"

        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal: {str(e)}")


@app.post("/api/research", response_model=ResearchResponse)
async def research(request: ResearchRequest, _: None = Depends(verify_api_key)):
    """Endpoint untuk mencari berita secara otomatis berdasarkan topik menggunakan Agentic AI."""
    try:
        result = await research_news_by_topic(request.topic)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal melakukan riset berita: {str(e)}")
