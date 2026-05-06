import os
import datetime
import logging
import json
import re
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

# Prompt yang dirampingkan
SYSTEM_PROMPT = (
    f"Anda adalah Research Assistant. Hari ini: {datetime.date.today().strftime('%d %b %Y')}\n"
    "Tugas: Cari berita terbaru via tool. Gunakan Bahasa Indonesia untuk field 'reason'.\n"
    "Aturan Ketat: Hanya pilih artikel yang BENAR-BENAR membahas topik utama secara langsung."
)

research_agent = Agent(
    'groq:llama-3.1-8b-instant',
    deps_type=ResearchDeps,
    output_type=ResearchResult,
    retries=2,
    system_prompt=SYSTEM_PROMPT,
)

@research_agent.tool
def search_tavily(ctx: RunContext[ResearchDeps], query: str) -> str:
    """Mencari berita di internet menggunakan Tavily."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key: return "Error: API Key tidak ada."
    
    try:
        tavily = TavilyClient(api_key=api_key)
        response = tavily.search(query=query, search_depth="advanced", topic="news", time_range="month", max_results=6)
        results = response.get("results", [])
        
        if results:
            ctx.deps.last_raw_results = results
            logger.info(f"Tavily returned {len(results)} results.")
        
        formatted = []
        for res in results:
            url = res.get('url', '').strip()
            if url: ctx.deps.verified_urls.add(url)
            formatted.append(f"T: {res.get('title')}\nU: {url}\nS: {res.get('content')[:300]}...\n---")
        
        return "\n".join(formatted) if formatted else "No results."
    except Exception as e:
        logger.error(f"Tavily Error: {str(e)}")
        return f"Error: {str(e)}"

def is_article_relevant(title: str, topic: str) -> bool:
    """Pengecekan kata kunci sederhana untuk menghindari hasil 'nyasar' (misal: BBM vs Nikel)."""
    keywords = re.findall(r'\w+', topic.lower())
    # Filter kata umum
    ignored = {'harga', 'kenaikan', 'indonesia', 'terbaru', 'update'}
    essential_keywords = [k for k in keywords if k not in ignored and len(k) > 2]
    
    if not essential_keywords: return True # Jika topik terlalu umum, skip filter
    
    title_lower = title.lower()
    return any(k in title_lower for k in essential_keywords)

async def research_news_by_topic(topic: str, on_progress: Optional[Callable[[str], None]] = None) -> ResearchResult:
    deps = ResearchDeps()
    all_verified_articles = []
    seen_urls = set()
    is_fallback_active = False
    
    # 1. Inisialisasi Data Awal
    if on_progress: on_progress(f"Mencari informasi awal tentang: {topic}...")
    try:
        mock_ctx = RunContext(agent=research_agent, deps=deps, model=None, usage=None, prompt_messages=[])
        search_tavily(mock_ctx, topic)
    except Exception as e:
        logger.error(f"Initial search failed: {str(e)}")
    
    # 2. Agentic Loop
    current_query = topic
    for attempt in range(1, 4):
        msg = f"Percobaan riset {attempt}: {current_query}"
        if on_progress: on_progress(msg)
        
        exclude_msg = f"\nExclude URLs: {list(seen_urls)}" if seen_urls else ""
        try:
            result = await research_agent.run(f"Topik: {current_query}. {exclude_msg}", deps=deps)
            
            new_articles = []
            for article in result.output.articles:
                clean_url = article.url.strip()
                # Verifikasi URL ada di hasil Tavily
                if any(clean_url.rstrip('/') == v_url.rstrip('/') for v_url in deps.verified_urls):
                    # Verifikasi Relevansi Judul (Anti-Nikel-for-BBM)
                    if is_article_relevant(article.title, topic):
                        norm_url = clean_url.rstrip('/').lower()
                        if norm_url not in seen_urls:
                            new_articles.append(article)
                            seen_urls.add(norm_url)
                    else:
                        logger.warning(f"Artikel ditolak karena tidak relevan: {article.title}")
            
            all_verified_articles.extend(new_articles)
            if len(all_verified_articles) >= 3: break # Target 3 artikel berkualitas
            if attempt < 3: current_query = result.output.suggested_query or f"{topic} terbaru"

        except Exception as e:
            logger.error(f"Attempt {attempt} failed: {str(e)}")
            if attempt == 3: break
            
    # 3. LOGIKA FALLBACK (Agresif)
    # Trigger fallback jika hasil kurang dari 2 atau tidak ada sama sekali
    if len(all_verified_articles) < 2 and deps.last_raw_results:
        is_fallback_active = True
        if on_progress: on_progress("Hasil terbatas ditemukan. Menampilkan hasil pencarian relevan lainnya...")
        
        # Kosongkan list untuk diisi hasil mentah Tavily agar user dapat semua data
        all_verified_articles = []
        for res in deps.last_raw_results:
            all_verified_articles.append(ResearchArticle(
                title=res.get('title', 'No Title'),
                source=res.get('url', '').split('/')[2] if res.get('url') else 'Source',
                url=res.get('url', ''),
                snippet=res.get('content', '')[:400] if res.get('content') else "No snippet available",
                reason="Hasil pencarian otomatis (Cadangan)",
                published_date=res.get('published_date') or "Unknown Date"
            ))
            
    return ResearchResult(articles=all_verified_articles[:6], suggested_query=None, is_fallback=is_fallback_active)
