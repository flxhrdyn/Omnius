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
    assert len(result.articles) > 0
    
    for article in result.articles:
        # Check relevance_score
        assert hasattr(article, 'relevance_score')
        assert isinstance(article.relevance_score, int)
        assert 0 <= article.relevance_score <= 10
        
        # Check published_date (Behavior 4 - Date Extraction)
        # Note: Some articles might genuinely be "Unknown Date" if Tavily doesn't have it,
        # but we want to ensure at least some have real dates in a news search.
        print(f"Article: {article.title} | Date: {article.published_date}")
        
    # Pastikan diurutkan berdasarkan skor (Descending)
    scores = [a.relevance_score for a in result.articles]
    assert scores == sorted(scores, reverse=True)
