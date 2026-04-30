import os
from typing import List
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from tavily import TavilyClient

# Skema output untuk hasil pencarian agent
class ResearchArticle(BaseModel):
    """Informasi artikel yang ditemukan oleh agent."""
    title: str = Field(description="Judul artikel berita")
    source: str = Field(description="Nama sumber berita atau domain (misal: CNN Indonesia, BBC, etc.)")
    url: str = Field(description="URL lengkap artikel")
    snippet: str = Field(description="Potongan teks atau ringkasan singkat isi artikel")
    reason: str = Field(description="Alasan mengapa agent memilih artikel ini untuk analisis framing")
    publishedDate: str = Field(default="Unknown Date", description="Tanggal dan jam publikasi artikel (jika ada)")

class ResearchResult(BaseModel):
    """Daftar artikel hasil riset agent."""
    articles: List[ResearchArticle] = Field(description="List 3-5 artikel terbaik yang ditemukan")

# Inisialisasi PydanticAI Agent
# Menggunakan awalan 'groq:' untuk integrasi native yang lebih simpel dan stabil
research_agent = Agent(
    'groq:llama-3.3-70b-versatile',
    output_type=ResearchResult,
    retries=3,
    system_prompt=(
        "Anda adalah News Research Assistant yang ahli dalam menemukan berita berkualitas tinggi "
        "untuk analisis framing media menggunakan metodologi Robert Entman. "
        "Tugas Anda adalah mencari artikel berita yang relevan dengan topik yang diberikan user. "
        "\n\nAturan Pencarian:"
        "\n1. Cari artikel dari sumber media yang kredibel. Identifikasi nama sumbernya (misal: Kompas, Tempo, Reuters)."
        "\n2. PENTING: Anda harus memilih URL artikel berita INDIVIDUAL, bukan halaman kumpulan berita (tag, topic, category, atau collection pages)."
        "\n3. Hindari URL yang mengandung '/tag/', '/topic/', '/category/', atau '/indeks/'. Pastikan URL merujuk langsung ke satu berita spesifik."
        "\n4. Usahakan mencari perspektif atau narasi yang berbeda (misal: satu pro, satu kontra, atau dari media dengan latar belakang berbeda)."
        "\n5. Hindari situs yang kemungkinan besar memiliki paywall atau sulit di-scrape."
        "\n6. Sertakan tanggal publikasi (publishedDate) jika tersedia dari hasil pencarian. Format publishedDate menjadi format 'DD MMM YYYY' (Contoh: 20 Feb 2026)."
        "\n7. Jika tanggal tidak tersedia secara eksplisit dari data tool, biarkan field tersebut sebagai 'Unknown Date'. Jangan menebak-nebak tanggal dari isi teks."
        "\n8. Pilih minimal 2 dan maksimal 5 artikel terbaik."
    ),
)

@research_agent.tool
def search_tavily(ctx: RunContext[None], query: str) -> str:
    """Mencari berita di internet menggunakan Tavily. 
    Gunakan tool ini untuk mendapatkan list artikel terbaru berdasarkan topik.
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY tidak dikonfigurasi."
    
    try:
        tavily = TavilyClient(api_key=api_key)
        # Menggunakan topic="news" dan time_range="week" untuk hasil terbaru (1 minggu terakhir)
        response = tavily.search(query=query, search_depth="advanced", topic="news", time_range="week", max_results=10)
        
        # Format hasil agar mudah dibaca oleh LLM
        results = []
        for res in response.get("results", []):
            pub_date = res.get('published_date') or "Not provided"
            results.append(f"Title: {res.get('title')}\nURL: {res.get('url')}\nDate: {pub_date}\nSnippet: {res.get('content')[:400]}...\n---")
        
        return "\n".join(results) if results else "Tidak ditemukan hasil pencarian."
    except Exception as e:
        return f"Terjadi kesalahan saat memanggil Tavily: {str(e)}"

async def research_news_by_topic(topic: str) -> ResearchResult:
    """Menjalankan agent untuk mencari berita berdasarkan topik.
    
    Args:
        topic: Topik atau isu berita yang ingin dicari.
        
    Returns:
        Objek ResearchResult berisi list artikel pilihan agent.
    """
    result = await research_agent.run(f"Cari berita terbaru mengenai topik ini: {topic}")
    return result.output
