import streamlit as st

from ui.utils.blog_markdown import merge_display_metadata, strip_frontmatter_for_display


def render_blog_preview(final_blog: str, metadata: dict):
    """Render blog preview with three tabs."""
    tab1, tab2, tab3 = st.tabs(["📖 Rendered Preview", "📝 Raw Markdown", "🏷️ Metadata"])

    display_meta = merge_display_metadata(final_blog, metadata)

    with tab1:
        _render_preview_tab(final_blog, display_meta)

    with tab2:
        st.code(final_blog, language="markdown")

    with tab3:
        st.json(display_meta)


def _render_preview_tab(final_blog: str, display_meta: dict):
    """Render the formatted blog preview."""
    word_count = int(display_meta.get("word_count") or 0)
    read_time = int(display_meta.get("read_time") or 0)
    tags = display_meta.get("tags") or []
    style = str(display_meta.get("style", "medium")).title()

    pills_html = f"""
    <div class="metadata-pills">
        <span class="pill pill-blue">📖 {read_time} min read</span>
        <span class="pill pill-green">📝 {word_count:,} words</span>
        <span class="pill pill-purple">🎨 {style}</span>
        {"".join(f'<span class="pill pill-orange">🏷️ {tag}</span>' for tag in tags[:4])}
    </div>
    """
    st.markdown(pills_html, unsafe_allow_html=True)

    blog_display = strip_frontmatter_for_display(final_blog)

    # One Streamlit block per open/close div leaves an empty box; use native bordered container.
    with st.container(border=True):
        st.markdown(blog_display)
