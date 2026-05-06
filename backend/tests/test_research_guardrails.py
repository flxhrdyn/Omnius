import os
os.environ["GROQ_API_KEY"] = "dummy_key"
os.environ["TAVILY_API_KEY"] = "dummy_key"

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.agent_service import research_news_by_topic, ResearchResult, ResearchArticle

@pytest.mark.asyncio
async def test_research_filters_hallucinated_urls():
    """
    Tes untuk memastikan URL yang tidak ada dalam verified_urls dibuang.
    """
    # Satu artikel valid, satu artikel halusinasi
    article_real = ResearchArticle(
        title="Berita Asli", 
        source="CNN", 
        url="https://cnn.com/real", 
        snippet="...", reason="...", 
        published_date="...",
        relevance_score=9
    )
    article_fake = ResearchArticle(
        title="Berita Palsu", 
        source="Hoax", 
        url="https://hoax.com/fake", 
        snippet="...", reason="...", 
        published_date="...",
        relevance_score=3
    )
    
    result = MagicMock()
    result.output = ResearchResult(articles=[article_real, article_fake], suggested_query=None)
    
    with patch("app.services.agent_service.research_agent.run", new_callable=AsyncMock) as mock_run, \
         patch("app.services.agent_service._execute_tavily_search") as mock_tavily:
        
        mock_run.return_value = result
        mock_tavily.return_value = [
            {"url": "https://cnn.com/real", "title": "Real A", "content": "Content Real"}
        ]
        
        # Hanya daftarkan URL asli di verified_urls
        with patch("app.services.agent_service.ResearchDeps") as mock_deps_class:
            mock_deps = MagicMock()
            mock_deps.verified_urls = {"https://cnn.com/real"}
            mock_deps_class.return_value = mock_deps
            
            final_result = await research_news_by_topic("topik test")
            
            # Verifikasi: Hanya artikel asli yang lolos
            assert len(final_result.articles) == 1
            assert final_result.articles[0].url == "https://cnn.com/real"
            # Artikel palsu harus dibuang
            assert not any(a.url == "https://hoax.com/fake" for a in final_result.articles)
