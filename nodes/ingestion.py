import logging
from models.state import RepoScribeState
from tools.github_tool import fetch_repo_data

logger = logging.getLogger(__name__)


def ingest_repo(state: RepoScribeState) -> RepoScribeState:
    """Fetch repository data from GitHub."""
    logger.info(f"Ingesting repo: {state['github_url']}")
    state["current_step"] = "ingestion"

    try:
        data = fetch_repo_data(state["github_url"])
        state.update(data)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        state["error"] = str(e)

    return state
