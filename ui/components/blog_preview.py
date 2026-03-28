import streamlit as st


def render_blog_preview(final_blog: str, metadata: dict):
    """Render blog preview with three tabs."""
    tab1, tab2, tab3 = st.tabs(["📖 Rendered Preview", "📝 Raw Markdown", "🏷️ Metadata"])

    with tab1:
        _render_preview_tab(final_blog, metadata)

    with tab2:
        st.code(final_blog, language="markdown")

    with tab3:
        st.json(metadata)


def _render_preview_tab(final_blog: str, metadata: dict):
    """Render the formatted blog preview."""
    # Metadata pills
    word_count = metadata.get("word_count", 0)
    read_time = metadata.get("read_time", 0)
    tags = metadata.get("tags", [])
    style = metadata.get("style", "medium").title()

    pills_html = f"""
    <div class="metadata-pills">
        <span class="pill pill-blue">📖 {read_time} min read</span>
        <span class="pill pill-green">📝 {word_count:,} words</span>
        <span class="pill pill-purple">🎨 {style}</span>
        {"".join(f'<span class="pill pill-orange">🏷️ {tag}</span>' for tag in tags[:4])}
    </div>
    """
    st.markdown(pills_html, unsafe_allow_html=True)

    # Strip YAML frontmatter for display
    blog_display = final_blog
    if blog_display.startswith("---"):
        parts = blog_display.split("---", 2)
        if len(parts) >= 3:
            blog_display = parts[2].strip()

    st.markdown('<div class="blog-preview-card">', unsafe_allow_html=True)
    st.markdown(blog_display)
    st.markdown("</div>", unsafe_allow_html=True)
