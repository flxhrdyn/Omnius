import os
import datetime
import logging
import json
import re
from typing import List, Optional, Callable, Dict
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
    reason: str = Field(description="Alasan singkat mengapa artikel ini relevan")
    published_date: str = Field(description="Tanggal publikasi (ekstrak dari data input jika tersedia)")
    relevance_score: int = Field(description="Skor relevansi (0-10) berdasarkan kecocokan konten dengan topik", ge=0, le=10)

class ResearchResult(BaseModel):
    articles: List[ResearchArticle] = Field(description="Daftar artikel yang sudah diurutkan berdasarkan relevansi")
    suggested_query: Optional[str] = Field(default=None, description="Saran kueri pencarian jika hasil saat ini kurang memadai")
    is_fallback: bool = False

class ResearchDeps:
    def __init__(self):
        self.verified_urls = set()
        self.raw_results_pool: Dict[str, dict] = {}

# Prompt Reranker
SYSTEM_PROMPT = (
    f"Anda adalah Smart News Reranker ({datetime.date.today()}).\n"
    "Tugas: Evaluasi daftar berita yang diberikan dan pilih yang paling relevan dengan topik.\n"
    "Aturan:\n"
    "1. Berikan skor 0-10 (10=Sangat Relevan, 0=Tidak Relevan).\n"
    "2. Ekstrak 'published_date' dari data input. Jika tidak ada, gunakan 'Unknown Date'.\n"
    "3. Gunakan Bahasa Indonesia untuk field 'reason'.\n"
    "4. Jika hasil kurang dari 3 yang relevan (skor > 7), berikan kueri baru yang lebih spesifik di field 'suggested_query'.\n"
    "5. DILARANG mengarang URL. Gunakan hanya URL yang tersedia di data input."
)

research_agent = Agent(
    'groq:llama-3.1-8b-instant',
    deps_type=ResearchDeps,
    output_type=ResearchResult,
    retries=1,
    system_prompt=SYSTEM_PROMPT,
)

def _execute_tavily_search(deps: ResearchDeps, query: str) -> str:
    """Fungsi internal untuk menjalankan pencarian Tavily tanpa dependensi RunContext."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key: return "Error: API Key tidak ada."
    
    try:
        tavily = TavilyClient(api_key=api_key)
        response = tavily.search(query=query, search_depth="advanced", topic="news", time_range="month", max_results=10)
        results = response.get("results", [])
        
        if results:
            for res in results:
                url = res.get('url', '').strip()
                if url:
                    deps.verified_urls.add(url)
                    if url not in deps.raw_results_pool:
                        deps.raw_results_pool[url] = res
        
        formatted = []
        for i, res in enumerate(results):
            date = res.get('published_date', 'Unknown Date')
            # Sertakan Tanggal (D) dalam konteks untuk LLM
            formatted.append(f"[{i}] T: {res.get('title')}\nD: {date}\nU: {res.get('url')}\nS: {res.get('content')[:350]}...\n---")
        
        return "\n".join(formatted) if formatted else "No results."
    except Exception as e:
        logger.error(f"Tavily Error: {str(e)}")
        return f"Error: {str(e)}"

@research_agent.tool
def search_tavily(ctx: RunContext[ResearchDeps], query: str) -> str:
    """Mencari berita di internet menggunakan Tavily."""
    return _execute_tavily_search(ctx.deps, query)

async def research_news_by_topic(topic: str, on_progress: Optional[Callable[[str], None]] = None) -> ResearchResult:
    deps = ResearchDeps()
    all_final_articles = []
    seen_urls = set()
    is_fallback_active = False
    
    current_query = topic
    for attempt in range(1, 3):
        msg = f"Riset (Attempt {attempt}/2): {current_query}"
        if on_progress: on_progress(msg)
        logger.info(msg)
        
        try:
            search_data = _execute_tavily_search(deps, current_query)
            
            if "No results" in search_data or "Error:" in search_data:
                if attempt == 1: 
                    current_query = f"{topic} news update"
                    continue
                else: break

            result = await research_agent.run(
                f"Topik: {topic}\n\nData Berita:\n{search_data}",
                deps=deps
            )
            
            valid_this_turn = []
            for article in result.output.articles:
                clean_url = article.url.strip()
                if any(clean_url.rstrip('/') == v_url.rstrip('/') for v_url in deps.verified_urls):
                    norm_url = clean_url.rstrip('/').lower()
                    if norm_url not in seen_urls and article.relevance_score >= 5:
                        valid_this_turn.append(article)
                        seen_urls.add(norm_url)
            
            all_final_articles.extend(valid_this_turn)
            
            high_quality = [a for a in valid_this_turn if a.relevance_score >= 8]
            if len(high_quality) >= 2 or len(all_final_articles) >= 4:
                break
                
            if attempt < 2:
                current_query = result.output.suggested_query or f"{topic} news update"

        except Exception as e:
            logger.error(f"Attempt {attempt} failed: {str(e)}")
            if attempt == 2: break

    # --- FINAL FALLBACK ---
    if len(all_final_articles) < 2 and deps.raw_results_pool:
        is_fallback_active = True
        if on_progress: on_progress("Mengaktifkan mode pencarian cadangan...")
        
        for url, res in deps.raw_results_pool.items():
            norm_url = url.rstrip('/').lower()
            if norm_url not in seen_urls:
                all_final_articles.append(ResearchArticle(
                    title=res.get('title', 'Berita'),
                    source=url.split('/')[2] if '/' in url else 'Sumber',
                    url=url,
                    snippet=res.get('content', '')[:350],
                    reason="Hasil pencarian otomatis (Cadangan)",
                    published_date=res.get('published_date') or "Unknown Date",
                    relevance_score=5
                ))
                seen_urls.add(norm_url)
                if len(all_final_articles) >= 10: break

    all_final_articles.sort(key=lambda x: x.relevance_score, reverse=True)
    
    return ResearchResult(
        articles=all_final_articles[:10], 
        suggested_query=None, 
        is_fallback=is_fallback_active
    )
