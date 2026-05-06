# PRD: Smart Reranking Research Agent (Stabilization)

## Problem Statement
Sistem riset sebelumnya yang berbasis *Multi-turn Reasoning* terbukti tidak stabil untuk model kecil seperti Llama 3.1 8B. Masalah utama meliputi halusinasi URL, kegagalan pemanggilan tool (400 Bad Request) akibat akumulasi konteks, serta ketidakakuratan pemilihan berita (misal: berita Nikel muncul untuk topik BBM). Pengguna membutuhkan sistem yang cepat, deterministik, namun tetap cerdas dalam membedah konten berita.

## Solution
Mengganti logika penalaran bebas menjadi alur **Deterministic Reranking** terstruktur. Sistem akan menarik pool berita yang lebih luas dari Tavily (10 hasil), lalu menggunakan LLM sebagai "Judge" untuk memberikan skor relevansi dan memilih artikel terbaik berdasarkan konten, bukan hanya berdasarkan skor mesin pencari.

## User Stories
1. As a researcher, I want a faster search process so that I don't waste time waiting for repetitive AI reasoning loops.
2. As a researcher, I want to see articles that are contextually relevant even if they have low search engine rankings, so I can discover hidden insights.
3. As a researcher, I want to see a relevance score for each article, so I can quickly prioritize which ones to analyze.
4. As a researcher, I want the system to automatically try a different search query if the first attempt yields no relevant results.
5. As a researcher, I want a guaranteed fallback to raw search results if the AI fails to find perfect matches, so I never lose access to data.

## Implementation Decisions

### 1. Smart Reranker Architecture
- **Single-Turn First**: Sistem melakukan pencarian kueri awal (10 hasil) dan langsung melakukan reranking dalam satu kali panggil LLM.
- **Content-Based Scoring**: LLM mengevaluasi Judul + Snippet (~300 karakter) dan memberikan skor relevansi (0-10).
- **Two-Attempt Limit**: Jika Attempt 1 menghasilkan < 2 artikel berkualitas (skor > 7), Agent akan menggunakan kueri saran LLM untuk mencoba Attempt 2.
- **Stateless Loop**: Setiap attempt bersifat independen tanpa menyimpan riwayat pesan untuk menghemat token dan menghindari rate limit.

### 2. Schema & API Changes
- **ResearchArticle**: Menambahkan field `relevance_score` (int) untuk indikator kualitas di UI.
- **Fallback Trigger**: Fallback otomatis aktif jika total artikel berkualitas dari semua attempt tetap di bawah ambang batas (threshold).

### 3. Verification & Safety
- **Manual Initial Search**: Sistem selalu melakukan pencarian mentah di awal untuk memastikan data cadangan (fallback) selalu siap di memori.
- **Strict URL Guardrails**: Tetap melakukan verifikasi URL terhadap hasil asli Tavily untuk mencegah halusinasi.

## Testing Decisions
- **Relevancy Tests**: Memastikan berita yang tidak nyambung (seperti Nickel untuk BBM) mendapatkan skor rendah dan difilter.
- **Latency Monitoring**: Memastikan 1 attempt selesai dalam waktu di bawah 5-8 detik.
- **Integration Test**: Memastikan frontend React dapat menampilkan skor relevansi dan flag fallback secara visual.

## Out of Scope
- Penarikan konten berita lengkap (full-text) selama fase riset (tetap berbasis snippet).
- Penambahan provider pencarian selain Tavily.

## Further Notes
Strategi ini mengalihkan beban kerja LLM dari "mencari cara untuk mendapatkan data" menjadi "menilai data yang sudah didapatkan", yang jauh lebih cocok untuk model 8B.
