import os
import json
import logging
from groq import Groq, APIError, RateLimitError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from app.models.schemas import NewsAnalysisModel
from app.core.config import FRAMING_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class NarrativeExtractor:
    """
    Module Deep untuk mengekstrak narasi berita menggunakan metodologi Robert Entman.
    Menyembunyikan detail LLM, prompt engineering, dan validasi skema dari caller.
    """
    
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.model_name = model_name
        self._client = self._get_groq_client()

    def _get_groq_client(self) -> Groq:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY tidak ditemukan di environment variables.")
        return Groq(api_key=api_key)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((APIError, RateLimitError))
    )
    def extract(self, text: str, title: str = "", url: str = "") -> NewsAnalysisModel:
        """
        Mengekstrak framing dari teks artikel.
        
        Interface: menerima teks dan metadata opsional.
        Implementation: mengelola komunikasi ke Groq, parsing JSON, dan fallback metadata.
        """
        completion = self._client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": FRAMING_SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        raw_json = completion.choices[0].message.content
        data = json.loads(raw_json)

        # Logika pembersihan metadata (Locality: perubahan logika sumber ada di sini)
        source = url.split("/")[2].replace("www.", "") if url and "/" in url else url or "Sumber Tidak Diketahui"
        
        if "title" not in data or not data["title"]:
            data["title"] = title or "Judul Tidak Tersedia"
        if "source" not in data or not data["source"]:
            data["source"] = source

        return NewsAnalysisModel.model_validate(data)
