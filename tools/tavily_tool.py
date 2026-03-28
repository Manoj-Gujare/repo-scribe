from langchain_community.tools.tavily_search import TavilySearchResults
from config.settings import get_settings


def get_tavily_tool():
    settings = get_settings()
    if not settings.TAVILY_API_KEY:
        return None
    return TavilySearchResults(
        max_results=5,
        api_key=settings.TAVILY_API_KEY,
    )
