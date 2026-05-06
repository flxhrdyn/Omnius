# PRD: Omnius Analysis & Research Stabilization (Fase 2)

## Problem Statement
Meskipun infrastruktur dasar sudah stabil (Fase 1), pengguna masih menghadapi kendala pada kualitas data dan pengalaman pengguna (UX) saat melakukan analisis:
1.  **AI Research Hallucination**: Agent sering memberikan URL berita yang tidak valid (404).
2.  **Low Relevancy (Noise)**: Hasil pencarian seringkali menyertakan link yang tidak relevan (seperti sidebar berita populer).
3.  **UI/UX Constraints**: Pengguna tidak bisa membatalkan (deselect) berita yang sudah dipilih, dan antrean riset seringkali bercampur secara membingungkan dengan antrean manual.

## Solution
Meningkatkan kualitas pipeline riset dan analisis melalui:
1.  **Hallucination Guardrails**: Verifikasi URL real-time terhadap data asli dari search engine (Tavily).
2.  **Agentic Relevancy Filter**: Menginstruksikan Agent untuk melakukan audit snippet dan hanya memilih artikel di mana topik menjadi subjek utama.
3.  **Decoupled Selection UX**: Memisahkan antrean seleksi untuk setiap metode input (Research, URL, Manual) agar kontrol lebih presisi.
4.  **Auto-Numbering**: Memberikan identitas otomatis pada input teks manual yang tidak memiliki judul.

## User Stories
1.  **Sebagai pengguna**, saya ingin sistem memverifikasi keaktifan link berita sebelum menampilkannya, agar saya terhindar dari link 404.
2.  **Sebagai pengguna**, saya ingin bisa membatalkan pilihan artikel di tab riset dengan mudah (toggle `+`/`x`).
3.  **Sebagai pengguna**, saya ingin input teks manual saya otomatis diberi judul (misal: "Berita 1") jika saya lupa memberikannya.
4.  **Sebagai pengguna**, saya ingin membatasi analisis maksimal 3 artikel untuk menjaga fokus dan performa.

## Implementation Decisions (Fase 2)
*   **Verified URL Guardrail**: Implementasi pengecekan di `agent_service.py` di mana URL Agent harus merupakan substring dari output asli tool.
*   **Decoupled Frontend State**: Menggunakan state `selectedResearchArticles` yang terpisah dari `urlInputs`.
*   **Toggle Logic UI**: Mengubah tombol seleksi menjadi interaktif (Select/Deselect).
*   **Independent Analysis Trigger**: Tombol "Jalankan Analisis" di setiap tab hanya memproses antrean spesifik dari tab tersebut.
*   **Auto-Titling**: Fallback judul dinamis di `ManualArticleProvider`.

## Testing Decisions
*   **Guardrail Unit Test**: Memverifikasi pemfilteran URL halusinasi.
*   **UX Toggle Test**: Memastikan penambahan dan penghapusan artikel di antrean riset berjalan sinkron dengan UI.
*   **Limit Enforcement Test**: Memastikan sistem menolak seleksi lebih dari 3 artikel.

## Out of Scope
*   Migrasi infrastruktur Azure (sudah selesai di Fase 1).
*   Implementasi sistem caching Redis.
*   Optimasi internal LLM Groq.
