import logging
from langgraph.graph import StateGraph, END
from models.state import RepoScribeState
from nodes.ingestion import ingest_repo
from nodes.analyzer import analyze_repo
from nodes.web_search import web_search_context
from nodes.outliner import generate_outline
from nodes.writer import write_blog
from nodes.formatter import format_output

logger = logging.getLogger(__name__)


def should_run_web_search(state: RepoScribeState) -> str:
    """Conditional edge: run web search only if Tavily is enabled."""
    if state.get("error"):
        return END
    return "web_search_context" if state.get("tavily_enabled") else "generate_outline"


def has_error(state: RepoScribeState) -> str:
    """Check if pipeline should stop due to error."""
    return END if state.get("error") else "analyze_repo"


_compiled_pipeline = None


def build_pipeline() -> StateGraph:
    """Build and compile the LangGraph pipeline (cached after first call)."""
    global _compiled_pipeline
    if _compiled_pipeline is not None:
        return _compiled_pipeline

    workflow = StateGraph(RepoScribeState)

    # Add nodes
    workflow.add_node("ingest_repo", ingest_repo)
    workflow.add_node("analyze_repo", analyze_repo)
    workflow.add_node("web_search_context", web_search_context)
    workflow.add_node("generate_outline", generate_outline)
    workflow.add_node("write_blog", write_blog)
    workflow.add_node("format_output", format_output)

    # Entry point
    workflow.set_entry_point("ingest_repo")

    # Conditional edge after ingestion (stop on error)
    workflow.add_conditional_edges(
        "ingest_repo",
        has_error,
        {END: END, "analyze_repo": "analyze_repo"},
    )

    # After analysis, conditionally run web search
    workflow.add_conditional_edges(
        "analyze_repo",
        should_run_web_search,
        {
            "web_search_context": "web_search_context",
            "generate_outline": "generate_outline",
            END: END,
        },
    )

    # Linear flow from web search onward
    workflow.add_edge("web_search_context", "generate_outline")
    workflow.add_edge("generate_outline", "write_blog")
    workflow.add_edge("write_blog", "format_output")
    workflow.add_edge("format_output", END)

    _compiled_pipeline = workflow.compile()
    return _compiled_pipeline


def run_pipeline(
    github_url: str,
    blog_style: str = "medium",
    blog_tone: str = "technical",
    tavily_enabled: bool = True,
    max_words: int = 1500,
) -> RepoScribeState:
    """Run the full pipeline and return final state."""
    from config.settings import get_settings
    settings = get_settings()

    initial_state: RepoScribeState = {
        "github_url": github_url,
        "blog_style": blog_style,
        "blog_tone": blog_tone,
        "repo_name": "",
        "repo_description": "",
        "readme": "",
        "file_tree": [],
        "key_files": {},
        "commits_summary": "",
        "languages": [],
        "repo_analysis": "",
        "tech_stack": [],
        "architecture_summary": "",
        "web_context": None,
        "blog_outline": {},
        "blog_sections": {},
        "final_blog": "",
        "metadata": {},
        "tavily_enabled": tavily_enabled and bool(settings.TAVILY_API_KEY),
        "max_words": max_words,
        "current_step": "starting",
        "error": None,
    }

    pipeline = build_pipeline()
    final_state = pipeline.invoke(initial_state)
    return final_state
