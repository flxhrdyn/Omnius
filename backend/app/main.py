"""
FastAPI Backend for News Framing Analysis
Menyediakan API endpoint yang menghubungkan React frontend
dengan logika scraping dan analisis Groq di Python.
"""

import os
import json
import logging
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, HTTPException, Request
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

# Konfigurasi CORS (Cross-Origin Resource Sharing)
# Kita gabungkan default dev dengan apa yang ada di .env
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://10.20.20.7:3000",
    "http://10.20.20.7:5173"
]

raw_origins = os.getenv("ALLOWED_ORIGINS", "")
if raw_origins:
    extra_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
    allowed_origins.extend(extra_origins)

# Hilangkan duplikasi
allowed_origins = list(set(allowed_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """Endpoint untuk mengecek apakah server berjalan."""
    return {"status": "ok", "message": "Omnius API is running."}


@app.get("/api/models")
def get_models():
    """Mengembalikan daftar model Groq yang tersedia."""
    return {"models": AVAILABLE_MODELS}


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
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
    for art in articles_data:
        if art.get("url"):
            providers.append(URLArticleProvider(art["url"]))
        else:
            providers.append(ManualArticleProvider(art.get("title", ""), art.get("text", "")))

    try:
        pipeline = AnalysisPipeline(request.model)
        
        def event_generator():
            for event in pipeline.run_stream(providers):
                yield f"data: {json.dumps(event)}\n\n"

        from fastapi.responses import StreamingResponse
        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal: {str(e)}")


@app.post("/api/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """Endpoint untuk mencari berita secara otomatis berdasarkan topik menggunakan Agentic AI."""
    try:
        result = await research_news_by_topic(request.topic)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal melakukan riset berita: {str(e)}")
