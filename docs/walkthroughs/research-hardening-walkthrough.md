# Walkthrough: Agentic Research Hardening & UX Stabilization

Dokumen ini merangkum perubahan besar pada sistem riset berita Omnius untuk meningkatkan stabilitas, transparansi, dan integritas data.

## Fitur Utama yang Diimplementasikan

### 1. Agentic Discovery Loop (Multi-turn)
Sistem riset tidak lagi hanya sekali tembak. Agent sekarang memiliki kemampuan untuk:
- Mengevaluasi hasil pencarian.
- Jika hasil kurang dari 2 artikel berkualitas, Agent merumuskan kueri baru dan mencoba lagi (maksimal 3x).
- Pada percobaan terakhir, Agent menggunakan strategi *Soft-Filtering* untuk mengambil hasil terbaik yang tersedia agar tidak kosong.

### 2. Deterministic URL Verification (Anti-Hallucination)
Untuk mencegah AI mengarang URL palsu atau link 404:
- Sistem mencatat setiap URL mentah yang dikembalikan oleh Tavily API.
- Hasil akhir Agent divalidasi silang terhadap daftar tersebut.
- Jika Agent mencoba memberikan URL di luar daftar tersebut, artikel otomatis dibuang oleh guardrail Python.

### 3. Progressive SSE Feedback
User tidak lagi menunggu dalam ketidakpastian. Status internal Agent dikirimkan secara real-time:
- `Percobaan riset 1: Mencari 'Topik X'...`
- `Berhasil menemukan 2 artikel...`
- `Mencoba kueri alternatif: 'Topik X terbaru'...`

### 4. UX Stabilization
- **Auto-Numbering**: Input manual tanpa judul otomatis diberi label "Berita 1", "Berita 2", dst.
- **Decoupled Selection**: Antrean artikel di tab Research, URL, dan Manual kini terpisah secara logis. Tombol analisis hanya memproses artikel dari tab yang aktif.

## Cara Verifikasi Lokal

1. **Jalankan Backend & Frontend** (Pastikan API Key sudah terpasang).
2. **Uji Topik Sulit**: Gunakan topik yang sangat spesifik untuk memicu mekanime *Retry*.
3. **Uji Manual Tanpa Judul**: Pastikan hasil ekstraksi framing di sidebar menampilkan judul otomatis yang rapi.
4. **Cek Integritas**: Pastikan link berita yang ditemukan Agent benar-benar mengarah ke portal berita asli.

## Status Teknis
- **Backend**: Python FastAPI dengan PydanticAI.
- **Model**: Llama 3.1 8B (Groq).
- **Frontend**: React + Tailwind.
- **Integritas**: 100% URL Verified.
