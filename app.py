import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="repo-scribe",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), "ui", "styles", "custom.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from ui.components.sidebar import render_sidebar, validate_github_url
from ui.components.progress_tracker import render_progress_tracker
from ui.components.blog_preview import render_blog_preview
from ui.components.export_panel import render_export_panel
from config.settings import get_settings


def init_session_state():
    defaults = {
        "pipeline_state": None,
        "blog_result": None,
        "step_statuses": {},
        "is_running": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def main():
    init_session_state()

    # Header
    st.markdown("""
    <div class="brand-header">
        <h1>📝 repo-scribe</h1>
        <p>Turn any GitHub repository into a publication-ready technical blog post</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    config = render_sidebar()

    # Validate environment
    settings = get_settings()
    env_ok = True

    if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
        st.error("AWS credentials not configured. Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `.env`.")
        env_ok = False

    if not settings.GITHUB_TOKEN:
        st.warning("GitHub token not set. Set `GITHUB_TOKEN` in `.env` for better rate limits.")

    # Handle generate button
    if config["generate_clicked"] and env_ok:
        is_valid, error_msg = validate_github_url(config["github_url"])
        if not is_valid:
            st.error(error_msg)
        else:
            st.session_state.is_running = True
            st.session_state.blog_result = None
            st.session_state.pipeline_state = None

    # Run pipeline
    if st.session_state.is_running and not st.session_state.blog_result:
        from graph.pipeline import run_pipeline

        progress_placeholder = st.empty()
        with progress_placeholder.container():
            render_progress_tracker("ingestion", config["tavily_enabled"])

        try:
            result = run_pipeline(
                github_url=config["github_url"],
                blog_style=config["blog_style"],
                blog_tone=config["blog_tone"],
                tavily_enabled=config["tavily_enabled"],
                max_words=config["max_words"],
            )
            st.session_state.blog_result = result
            st.session_state.is_running = False
        except Exception as e:
            st.session_state.is_running = False
            with progress_placeholder.container():
                render_progress_tracker("ingestion", config["tavily_enabled"], error=str(e))
            st.button("Retry", on_click=lambda: st.session_state.update({"is_running": True, "blog_result": None}))
            st.stop()

        progress_placeholder.empty()

    # Show results
    result = st.session_state.blog_result
    if result:
        if result.get("error"):
            render_progress_tracker(result.get("current_step", ""), config["tavily_enabled"], error=result["error"])
            if st.button("Retry"):
                st.session_state.is_running = True
                st.session_state.blog_result = None
                st.rerun()
        else:
            render_progress_tracker("done", config["tavily_enabled"])
            st.success("Blog generated successfully!")

            render_export_panel(result.get("final_blog", ""), result.get("repo_name", ""))
            st.divider()
            render_blog_preview(result.get("final_blog", ""), result.get("metadata", {}))
    elif not st.session_state.is_running:
        st.info("Enter a GitHub URL in the sidebar and click **Generate Blog** to get started.")


if __name__ == "__main__":
    main()
