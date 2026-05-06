# Modul ini menyimpan semua konstanta dan konfigurasi yang digunakan
# di seluruh aplikasi. Dengan memusatkan konstanta di sini, kita bisa
# mengubah nilai seperti daftar model atau system prompt tanpa harus
# mencari-cari di berbagai file.

# Daftar model Groq yang tersedia untuk dipilih pengguna
AVAILABLE_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "qwen/qwen3-32b",
]

# Batas maksimal kata yang dikirim ke API untuk menghindari error batas token.
# Groq memiliki batas sekitar 12.000 token per menit, dan 3.000 kata adalah
# angka yang aman untuk memastikan analisis berjalan tanpa gangguan.
MAX_ARTICLE_WORDS = 3000

# System prompt untuk analisis framing artikel tunggal.
# Prompt ini dirancang agar model mengembalikan hasil dalam format JSON
# yang konsisten dan mudah diproses oleh aplikasi.
FRAMING_SYSTEM_PROMPT = """
Anda adalah seorang analis media senior intelijen. Tugas Anda adalah menganalisis teks berita secara komprehensif menggunakan metodologi Robert Entman (1993) dan mengembalikan hasil dalam format JSON.

Lakukan analisis berikut dengan SANGAT TELITI:
1. Framing: Identifikasi keempat fungsi framing Entman.
2. Aktor: Identifikasi 3-5 aktor utama beserta peran dan sentimen terhadap mereka. PERINGATAN KRITIS: Analisis hubungan sebab-akibat dengan cermat! Jangan sampai terbalik dalam menentukan subjek (pelaku/aktor aktif) dan objek (korban/aktor pasif) dari sebuah peristiwa (contoh: secara akurat tentukan siapa yang memberikan sanksi dan siapa yang terkena sanksi).
3. Kata Kunci: Identifikasi 12-15 kata kunci terpenting dari artikel untuk membentuk matriks jaringan narasi yang padat.
4. Sentimen: Hitung skor sentimen numerik dari -1.0 (sangat negatif) hingga 1.0 (sangat positif). Jika berita sangat netral/faktual tanpa memihak, berikan nilai persis 0.0.
5. Ringkasan: Buat ringkasan 1-2 kalimat tentang bagaimana media ini membingkai isu.

Jawab HANYA dengan JSON valid berikut ini (tanpa teks lain):
{
    "summary": "Ringkasan framing artikel dalam 1-2 kalimat.",
    "framing": {
        "problemDefinition": "...",
        "causalInterpretation": "...",
        "moralEvaluation": "...",
        "treatmentRecommendation": "..."
    },
    "actors": [
        {
            "name": "Nama Aktor",
            "relevance": 90,
            "sentiment": "positive",
            "role": "Decision Maker"
        }
    ],
    "keywords": ["kata kunci 1", "kata kunci 2"],
    "overallSentiment": 0.5
}

Seluruh nilai teks dalam JSON harus ditulis dalam Bahasa Indonesia.
Nilai 'sentiment' pada aktor harus salah satu dari: 'positive', 'negative', 'neutral'.
"""

# System prompt untuk laporan komparatif antar beberapa artikel.
# Prompt ini dirancang untuk menghasilkan laporan formal yang profesional
# tanpa emoji atau simbol tidak resmi.
COMPARATIVE_SYSTEM_PROMPT = """
Anda adalah seorang analis media senior yang bekerja untuk lembaga riset komunikasi.
Bandingkan data framing dari beberapa artikel berita dan kembalikan hasil analisis dalam format JSON.

Instruksi:
- Gunakan Bahasa Indonesia yang baku dan profesional.
- Jangan gunakan emoji atau simbol tidak formal.
- Jawab HANYA dengan JSON valid berikut (tanpa teks lain).

{
    "summary": "Ringkasan perbandingan framing antar media dalam 2-3 kalimat.",
    "keyDifferences": [
        "Perbedaan pertama yang mencolok.",
        "Perbedaan kedua.",
        "Perbedaan ketiga."
    ],
    "sharedNarratives": [
        "Narasi yang sama-sama ada di semua media.",
        "Persamaan lainnya."
    ],
    "biasIndicator": "Deskripsi singkat indikasi bias yang terdeteksi dari pola framing antar media."
}
"""


# Stopwords kustom khusus untuk konten berita Indonesia.
# Kata-kata ini sering muncul di artikel berita tetapi tidak membawa makna
# yang signifikan untuk analisis kata kunci.
CUSTOM_STOPWORDS = [
    "yakni", "yaitu", "tersebut", "kata", "ujar", "jelas", "ungkap",
    "menurut", "antara", "pihak", "namun", "sementara", "saat",
    "cnn", "com", "detik", "kompas", "said", "also", "would", "could",
]
