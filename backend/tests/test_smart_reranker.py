import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.agent_service import research_news_by_topic, ResearchResult, ResearchArticle

@pytest.mark.asyncio
async def test_reranker_assigns_relevance_scores():
    """
    Memastikan sistem memberikan skor relevansi (relevance_score) pada setiap artikel.
    """
    topic = "Kenaikan harga BBM di Indonesia"
    
    # Mock articles
    article1 = ResearchArticle(
        title="BBM Naik 1", source="Source 1", url="http://s1.com", snippet="...", reason="...", 
        published_date="2026-05-01", relevance_score=10
    )
    article2 = ResearchArticle(
        title="BBM Naik 2", source="Source 2", url="http://s2.com", snippet="...", reason="...", 
        published_date="2026-05-02", relevance_score=8
    )
    
    mock_agent_result = MagicMock()
    mock_agent_result.output = ResearchResult(articles=[article1, article2], suggested_query=None)

    with patch("app.services.agent_service.research_agent.run", new_callable=AsyncMock) as mock_run, \
         patch("app.services.agent_service._execute_tavily_search") as mock_tavily, \
         patch("app.services.agent_service.ResearchDeps") as mock_deps_class:
        
        mock_run.return_value = mock_agent_result
        mock_tavily.return_value = [
            {"url": "http://s1.com", "title": "S1", "content": "C1"},
            {"url": "http://s2.com", "title": "S2", "content": "C2"}
        ]
        mock_deps = MagicMock()
        mock_deps.verified_urls = {"http://s1.com", "http://s2.com"}
        mock_deps_class.return_value = mock_deps

        # Jalankan riset
        result = await research_news_by_topic(topic)
        
        # Verifikasi tipe output
        assert isinstance(result, ResearchResult)
        assert len(result.articles) == 2
        
        for article in result.articles:
            # Check relevance_score
            assert hasattr(article, 'relevance_score')
            assert isinstance(article.relevance_score, int)
            assert 0 <= article.relevance_score <= 10
            
        # Pastikan diurutkan berdasarkan skor (Descending)
        scores = [a.relevance_score for a in result.articles]
        assert scores == sorted(scores, reverse=True)
