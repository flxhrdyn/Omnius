import os
import datetime
import logging
import json
from typing import List, Optional, Callable
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from tavily import TavilyClient

# Konfigurasi Logging
logger = logging.getLogger(__name__)

# Skema output (SNAKE_CASE)
class ResearchArticle(BaseModel):
    title: str = Field(description="Judul berita")
    source: str = Field(description="Nama sumber/domain")
    url: str = Field(description="URL lengkap")
    snippet: str = Field(description="Ringkasan singkat")
    reason: str = Field(description="Alasan (Bahasa Indonesia)")
    published_date: str = Field(default="Unknown Date")

class ResearchResult(BaseModel):
    articles: List[ResearchArticle] = Field(description="Daftar artikel")
    suggested_query: Optional[str] = Field(default=None)
    is_fallback: bool = False

class ResearchDeps:
    def __init__(self):
        self.verified_urls = set()
        self.last_raw_results = []

# Prompt yang sangat ringkas untuk kecepatan
SYSTEM_PROMPT = (
    f"Anda adalah News Assistant ({datetime.date.today()}).\n"
    "Cari berita terbaru via tool. Gunakan Bahasa Indonesia untuk field 'reason'.\n"
    "PENTING: Hanya berikan URL yang benar-benar ada di hasil pencarian."
)

research_agent = Agent(
    'groq:llama-3.1-8b-instant',
    deps_type=ResearchDeps,
    output_type=ResearchResult,
    retries=1,
    system_prompt=SYSTEM_PROMPT,
)

@research_agent.tool
def search_tavily(ctx: RunContext[ResearchDeps], query: str) -> str:
    """Mencari berita di internet menggunakan Tavily."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key: return "Error: API Key tidak ada."
    
    try:
        tavily = TavilyClient(api_key=api_key)
        # Ambil 5 hasil saja agar cepat
        response = tavily.search(query=query, search_depth="advanced", topic="news", time_range="month", max_results=5)
        results = response.get("results", [])
        
        if results:
            ctx.deps.last_raw_results = results
            for res in results:
                url = res.get('url', '').strip()
                if url: ctx.deps.verified_urls.add(url)
        
        formatted = [f"T: {r.get('title')}\nU: {r.get('url')}\nS: {r.get('content')[:200]}..." for r in results]
        return "\n---\n".join(formatted) if formatted else "No results."
    except Exception as e:
        logger.error(f"Tavily Error: {str(e)}")
        return "Gagal mencari berita."

async def research_news_by_topic(topic: str, on_progress: Optional[Callable[[str], None]] = None) -> ResearchResult:
    deps = ResearchDeps()
    all_verified_articles = []
    seen_urls = set()
    is_fallback_active = False
    
    # Percobaan dikurangi menjadi 2 agar lebih cepat
    current_query = topic
    for attempt in range(1, 3):
        msg = f"Riset ({attempt}/2): {current_query}"
        if on_progress: on_progress(msg)
        
        try:
            # Gunakan mode stateless tanpa history
            result = await research_agent.run(f"Cari: {current_query}", deps=deps)
            
            for article in result.output.articles:
                clean_url = article.url.strip()
                # Cek verifikasi URL sederhana
                if any(clean_url.rstrip('/') == v_url.rstrip('/') for v_url in deps.verified_urls):
                    norm_url = clean_url.rstrip('/').lower()
                    if norm_url not in seen_urls:
                        all_verified_articles.append(article)
                        seen_urls.add(norm_url)
            
            if len(all_verified_articles) >= 2: break
            current_query = f"{topic} terbaru"

        except Exception as e:
            logger.error(f"Attempt {attempt} error: {str(e)}")
            if attempt == 2: break
            
    # FALLBACK: Jika Agent gagal, tampilkan hasil mentah Tavily apa adanya
    if not all_verified_articles and deps.last_raw_results:
        is_fallback_active = True
        if on_progress: on_progress("Menampilkan hasil pencarian cadangan...")
        
        for res in deps.last_raw_results:
            all_verified_articles.append(ResearchArticle(
                title=res.get('title', 'Berita'),
                source=res.get('url', '').split('/')[2] if res.get('url') else 'Sumber',
                url=res.get('url', ''),
                snippet=res.get('content', '')[:300],
                reason="Hasil pencarian otomatis (Fallback)",
                published_date=res.get('published_date') or "Baru saja"
            ))
            
    return ResearchResult(articles=all_verified_articles[:5], suggested_query=None, is_fallback=is_fallback_active)
