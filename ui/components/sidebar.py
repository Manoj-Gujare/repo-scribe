import re
import streamlit as st
from config.settings import get_settings


def render_sidebar() -> dict:
    """Render sidebar inputs and return configuration dict."""
    settings = get_settings()

    with st.sidebar:
        st.markdown("""
        <div style="padding: 1rem 0; border-bottom: 1px solid #2d2d4e; margin-bottom: 1.5rem;">
            <h2 style="color: white; margin: 0; font-size: 1.4rem;">📝 repo-scribe</h2>
            <p style="color: #a0a0b0; margin: 0.3rem 0 0 0; font-size: 0.8rem;">Powered by AWS Bedrock</p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Repository")
        github_url = st.text_input(
            "GitHub URL",
            placeholder="https://github.com/owner/repo",
            help="Enter the full URL of a public GitHub repository",
        )

        st.subheader("Blog Settings")
        blog_style = st.radio(
            "Style",
            options=["medium", "towardsdatascience"],
            format_func=lambda x: "Medium" if x == "medium" else "Towards Data Science",
            horizontal=True,
        )

        blog_tone = st.selectbox(
            "Tone",
            options=["technical", "intermediate", "beginner-friendly"],
            format_func=lambda x: x.replace("-", " ").title(),
        )

        max_words = st.slider(
            "Max Words",
            min_value=800,
            max_value=2500,
            value=settings.MAX_BLOG_WORDS,
            step=100,
        )

        # Tavily status indicator
        tavily_enabled = bool(settings.TAVILY_API_KEY)
        if tavily_enabled:
            st.success("🟢 Web Search Enabled")
        else:
            st.warning("🔴 Web Search Disabled\n\nSet `TAVILY_API_KEY` in `.env` to enable.")

        st.divider()
        generate_clicked = st.button("Generate Blog", type="primary", use_container_width=True)

    return {
        "github_url": github_url,
        "blog_style": blog_style,
        "blog_tone": blog_tone,
        "max_words": max_words,
        "tavily_enabled": tavily_enabled,
        "generate_clicked": generate_clicked,
    }


def validate_github_url(url: str) -> tuple[bool, str]:
    """Validate GitHub URL format."""
    if not url:
        return False, "Please enter a GitHub URL."
    pattern = r"^https://github\.com/[\w\-\.]+/[\w\-\.]+/?$"
    if not re.match(pattern, url):
        return False, f"Invalid GitHub URL: `{url}`. Format: `https://github.com/owner/repo`"
    return True, ""
