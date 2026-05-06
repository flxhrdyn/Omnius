import os
from dotenv import load_dotenv

# Load env vars BEFORE importing agent_service
load_dotenv()

import pytest
from app.services.agent_service import research_news_by_topic, ResearchResult

@pytest.mark.asyncio
async def test_reranker_assigns_relevance_scores():
    """
    Memastikan sistem memberikan skor relevansi (relevance_score) pada setiap artikel.
    """
    topic = "Kenaikan harga BBM di Indonesia"
    
    # Jalankan riset
    result = await research_news_by_topic(topic)
    
    # Verifikasi tipe output
    assert isinstance(result, ResearchResult)
    
    # Verifikasi bahwa artikel memiliki field relevance_score
    assert len(result.articles) > 0, "Harus ada minimal satu artikel yang ditemukan atau fallback"
    
    for article in result.articles:
        assert hasattr(article, 'relevance_score'), f"Artikel '{article.title}' tidak punya relevance_score"
        assert isinstance(article.relevance_score, int)
        assert 0 <= article.relevance_score <= 10
        
    # Pastikan diurutkan berdasarkan skor (Descending)
    scores = [a.relevance_score for a in result.articles]
    assert scores == sorted(scores, reverse=True), "Artikel harus diurutkan dari skor tertinggi ke terendah"
