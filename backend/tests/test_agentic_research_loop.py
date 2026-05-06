import os
os.environ["GROQ_API_KEY"] = "dummy_key"
os.environ["TAVILY_API_KEY"] = "dummy_key"

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.agent_service import research_news_by_topic, ResearchResult, ResearchArticle

@pytest.mark.asyncio
async def test_research_loops_until_quota_met():
    """
    Tes untuk memastikan research_news_by_topic melakukan retry jika jumlah artikel < 2.
    """
    # Mocking respons Agent
    # Percobaan 1: Kosong, menyarankan kueri baru
    result1 = MagicMock()
    result1.output = ResearchResult(articles=[], suggested_query="kueri alternatif")
    
    # Percobaan 2: Dapat 2 artikel
    article1 = ResearchArticle(
        title="Berita 1", 
        source="Source A", 
        url="https://news-a.com/1", 
        snippet="Snippet 1", 
        reason="Reason 1",
        publishedDate="01 May 2026"
    )
    article2 = ResearchArticle(
        title="Berita 2", 
        source="Source B", 
        url="https://news-b.com/2", 
        snippet="Snippet 2", 
        reason="Reason 2",
        publishedDate="02 May 2026"
    )
    result2 = MagicMock()
    result2.output = ResearchResult(articles=[article1, article2], suggested_query=None)
    
    # Patching research_agent.run
    with patch("app.services.agent_service.research_agent.run", new_callable=AsyncMock) as mock_run:
        mock_run.side_effect = [result1, result2]
        
        # Patching verified_urls di deps agar URL dianggap valid
        with patch("app.services.agent_service.ResearchDeps") as mock_deps_class:
            mock_deps = MagicMock()
            mock_deps.verified_urls = {"https://news-a.com/1", "https://news-b.com/2"}
            mock_deps_class.return_value = mock_deps
            
            # Eksekusi
            final_result = await research_news_by_topic("topik test")
            
            # Verifikasi: Harus memanggil agent.run sebanyak 2 kali
            assert mock_run.call_count == 2
            assert len(final_result.articles) == 2
            assert final_result.articles[0].title == "Berita 1"
            assert final_result.articles[1].title == "Berita 2"
