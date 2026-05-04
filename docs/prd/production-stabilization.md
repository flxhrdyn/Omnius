# PRD: Produksi & Stabilisasi Infrastruktur Omnius

## Problem Statement
Pengguna (terutama pada tier **Azure Students**) mengalami masalah **Cold Start** yang menyebabkan aplikasi terasa "mati" atau sangat lambat saat pertama kali dibuka. Selain itu, proses analisis framing yang memakan waktu lama seringkali terputus di tengah jalan karena **Idle Timeout** (230 detik) pada Load Balancer Azure, sehingga hasil riset tidak muncul secara utuh.

## Solution
Mengimplementasikan strategi stabilisasi tiga lapis:
1.  **Backend Stability**: Menambahkan SSE Heartbeat dan optimasi logging untuk menjaga koneksi tetap hidup.
2.  **Frontend Pre-warming**: Membangunkan container Azure secara proaktif saat user pertama kali mendarat di landing page.
3.  **Infrastructure Efficiency**: Mengecilkan ukuran image Docker menggunakan Multi-stage build untuk mempercepat waktu start-up.

## User Stories
1.  **Sebagai pengguna**, saya ingin aplikasi tetap responsif meskipun sudah lama tidak digunakan, sehingga saya tidak menganggap aplikasi rusak.
2.  **Sebagai pengguna**, saya ingin proses analisis framing yang kompleks tidak terputus di tengah jalan, sehingga saya bisa mendapatkan laporan intelijen yang lengkap.
3.  **Sebagai pengembang**, saya ingin dokumentasi keputusan arsitektur (ADR) tersedia dengan jelas, sehingga saya tidak bingung saat melakukan pemeliharaan di masa depan.
4.  **Sebagai pengembang**, saya ingin image Docker sekecil mungkin, sehingga proses CI/CD dan deployment ke Azure ACR berjalan lebih cepat.

## Implementation Decisions
*   **Heartbeat Mechanism**: Backend FastAPI akan mengirimkan komentar `: keep-alive` setiap 15 detik pada stream SSE jika tidak ada data baru yang dikirim. (Status: **Selesai**)
*   **Pre-warming Strategy**: Frontend React akan memanggil `GET /api/health` secara asinkron (non-blocking) pada saat *initial mount* komponen utama. (Status: **Selesai**)
*   **Docker Optimization**: Mengadopsi **Multi-stage build** di Dockerfile untuk memisahkan tahap kompilasi/dependensi dengan tahap runtime, mengurangi ukuran image akhir secara signifikan. (Status: **Selesai**)
*   **Security Enforcement**: Mempertahankan `X-API-Key` sebagai satu-satunya metode otentikasi antar-layanan (Netlify ke Azure). (Status: **Selesai**)

## Testing Decisions
*   **SSE Stability Test**: Melakukan simulasi analisis yang memakan waktu > 4 menit untuk memastikan koneksi tidak terputus.
*   **Cold Start Latency Measurement**: Mengukur waktu respons request pertama setelah container dimatikan secara manual (idle simulation).
*   **Image Size Audit**: Memastikan image akhir di ACR tidak mengandung dependensi build (seperti `build-essential` atau `git`).

## Out of Scope
*   Migrasi ke plan Azure berbayar (B1 atau lebih tinggi).
*   Implementasi Redis atau sistem caching database (untuk saat ini).
*   Optimasi performa model LLM itu sendiri (karena menggunakan API Groq eksternal).

## Further Notes
Implementasi ini ditujukan khusus untuk mengoptimalkan resource gratis pada Azure Students agar memiliki User Experience yang setara dengan infrastruktur produksi profesional.
