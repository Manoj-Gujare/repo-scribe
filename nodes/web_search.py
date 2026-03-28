import logging
from datetime import datetime

from models.state import RepoScribeState
from tools.tavily_tool import get_tavily_tool

logger = logging.getLogger(__name__)


def web_search_context(state: RepoScribeState) -> RepoScribeState:
    """Enrich blog with web search results using Tavily."""
    if state.get("error"):
        return state

    logger.info("Running web search enrichment...")
    state["current_step"] = "web_search"

    tool = get_tavily_tool()
    if tool is None:
        state["web_context"] = None
        return state

    repo_name = state.get("repo_name", "")
    tech_stack = state.get("tech_stack", [])
    tech_str = " ".join(tech_stack[:3]) if tech_stack else ""

    year = datetime.now().year
    queries = [
        f"{repo_name} {tech_str} tutorial",
        f"{tech_str} open source tools",
        f"{tech_str} best practices {year}",
    ]

    results = []
    for query in queries:
        try:
            search_results = tool.invoke(query)
            if isinstance(search_results, list):
                for r in search_results[:2]:
                    if isinstance(r, dict):
                        title = r.get("title", "")
                        content = r.get("content", "")[:300]
                        url = r.get("url", "")
                        results.append(f"**{title}**\n{content}\n{url}")
        except Exception as e:
            logger.warning(f"Search query failed for '{query}': {e}")

    state["web_context"] = "\n\n".join(results) if results else None
    return state
