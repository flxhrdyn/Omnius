# PRD: Agentic Research Hardening & UX Stabilization

## Problem Statement
Sistem riset berita saat ini rentan terhadap halusinasi AI (URL palsu/mati), kurang transparan dalam proses pencarian (user tidak tahu apa yang dilakukan Agent), dan memiliki kontrol seleksi yang membingungkan karena antrean artikel yang bercampur antar metode input.

## Solution
Mentransformasi riset berita menjadi **Agentic Assistant** yang deterministik. Sistem akan melakukan pencarian iteratif (Multi-turn Loop), memvalidasi setiap URL secara fisik terhadap hasil mentah search engine, memberikan progres real-time melalui SSE, dan memisahkan antrean seleksi untuk kontrol pengguna yang maksimal.

## User Stories
1. Sebagai analis, saya ingin Agent melakukan pencarian ulang secara otomatis jika hasil awal tidak relevan, sehingga saya mendapatkan data berkualitas tanpa input manual tambahan.
2. Sebagai analis, saya ingin melihat progres langkah demi langkah Agent ("Mencari...", "Mencoba kueri lain...") agar saya tahu sistem sedang bekerja dan tidak macet.
3. Sebagai analis, saya ingin jaminan bahwa setiap link berita yang diberikan Agent adalah link asli yang aktif, bukan karangan AI.
4. Sebagai analis, saya ingin ringkasan alasan pemilihan berita dalam Bahasa Indonesia, namun tetap melihat potongan berita asli dalam bahasa sumbernya untuk menjaga integritas informasi.
5. Sebagai analis, saya ingin antrean berita hasil riset terpisah dari daftar URL manual saya, agar saya bisa memilih dengan presisi artikel mana yang akan masuk ke tahap framing.
6. Sebagai analis, saya ingin input teks manual saya otomatis diberi nomor jika saya lupa memberi judul, agar laporan akhir tetap rapi.

## Implementation Decisions

### 1. Agentic Loop & Multi-turn Strategy
- **Iterasi Maksimal**: 3 kali percobaan pencarian.
- **Multi-turn Reasoning**: Agent diwajibkan menyarankan kueri alternatif jika hasil pada iterasi saat ini kurang dari kuota (2 artikel).
- **Soft-Filtering (Attempt 3)**: Pada percobaan terakhir, Agent diinstruksikan untuk menurunkan standar relevansi guna menghindari daftar kosong, namun tetap jujur memberikan catatan jika artikel adalah "pilihan terbaik yang tersedia".

### 2. Guardrails & Honesty
- **Deterministic URL Verification**: Kode sistem akan melakukan *cross-check* setiap URL Agent terhadap daftar URL mentah dari Tavily API. URL yang tidak cocok akan dibuang secara otomatis sebelum sampai ke User.
- **Date Awareness**: System prompt menyertakan tanggal hari ini (`today()`) untuk memberikan konteks temporal yang akurat bagi Agent.
- **Honesty Instruction**: Instruksi ketat melarang Agent memalsukan tanggal atau mengarang artikel jika data tidak ditemukan.

### 3. Language & Output Policy
- **Snippet (Potongan Berita)**: Harus dipertahankan dalam **bahasa asli** sumber (misal: Inggris) untuk menghindari bias terjemahan pada data mentah.
- **Reason (Alasan Pemilihan)**: Disajikan dalam **Bahasa Indonesia** untuk kenyamanan analisis cepat.
- **Final Analysis (Framing Report)**: Seluruh narasi laporan dalam **Bahasa Indonesia**, kecuali field teknis (Actors, Keyword Matrix, Sensitive Keywords).

### 4. Technical Constraints
- **Model**: Groq `llama-3.1-8b-instant` (High speed, low latency).
- **Search Provider**: Tavily API dengan parameter `search_depth="advanced"`, `topic="news"`, dan `time_range="month"`.
- **Progress Tracking**: Menggunakan SSE (Server-Sent Events) untuk mengirim pesan status dari Agent ke UI.

### 5. UX Stabilization
- **Decoupled Selection**: Memisahkan state seleksi untuk tab Research, URL, dan Manual.
- **Auto-Numbering**: Logika backend untuk memberikan judul otomatis ("Berita 1", "Berita 2") jika input manual tidak memiliki judul.

## Testing Decisions
- **Loop Testing**: Unit test menggunakan mock untuk mensimulasikan kegagalan pencarian dan memverifikasi bahwa Agent melakukan retry dengan kueri yang berbeda.
- **Guardrail Testing**: Verifikasi bahwa URL halusinasi dibuang oleh sistem deteksi URL.

## Out of Scope
- Pencarian video atau konten media sosial (fokus tetap pada portal berita).
- Analisis sentimen real-time selama proses riset (analisis dilakukan di tahap framing).
