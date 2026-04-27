"""
FastAPI Backend for News Framing Analysis
Menyediakan API endpoint yang menghubungkan React frontend
dengan logika scraping dan analisis Groq di Python.
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Muat environment variables dari .env di root project
load_dotenv()

from app.services.analyzer import run_full_analysis
from app.core.config import AVAILABLE_MODELS

app = FastAPI(
    title="Omnius API",
    description="API backend untuk analisis framing berita menggunakan Groq LLM.",
    version="1.0.0",
)

# Izinkan request dari mana saja (CORS) untuk development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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

    try:
        result = run_full_analysis(articles_data, request.model)
        return result.model_dump()

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal: {str(e)}")
