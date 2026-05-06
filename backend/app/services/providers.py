from abc import ABC, abstractmethod
from typing import Optional, Tuple
from app.services.scraper import scrape_article

class ArticleProvider(ABC):
    """
    Interface (Seam) untuk mendapatkan konten berita.
    Implementasi konkret (Adapter) akan menangani detail cara pengambilannya.
    """
    
    @abstractmethod
    def get_content(self) -> Tuple[str, str, Optional[str]]:
        """
        Mengembalikan tuple: (title, text, error_message)
        """
        pass

class URLArticleProvider(ArticleProvider):
    """Adapter untuk mengambil berita dari URL (Scraping)."""
    def __init__(self, url: str):
        self.url = url

    def get_content(self) -> Tuple[str, str, Optional[str]]:
        return scrape_article(self.url)

class ManualArticleProvider(ArticleProvider):
    """Adapter untuk berita yang dimasukkan secara manual (Full Text)."""
    def __init__(self, title: str, text: str, fallback_title: str = "Judul Manual"):
        self.title = title
        self.text = text
        self.fallback_title = fallback_title

    def get_content(self) -> Tuple[str, str, Optional[str]]:
        if not self.text:
            return "", "", "Teks berita manual kosong."
        return self.title or self.fallback_title, self.text, None
