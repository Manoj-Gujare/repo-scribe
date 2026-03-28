import streamlit as st


def render_export_panel(final_blog: str, repo_name: str):
    """Render export options for the generated blog."""
    st.subheader("Export")

    col1, col2, col3 = st.columns(3)

    filename = f"{repo_name.replace('/', '-')}_blog.md" if repo_name else "blog.md"

    with col1:
        st.download_button(
            label="📥 Download .md",
            data=final_blog,
            file_name=filename,
            mime="text/markdown",
            use_container_width=True,
        )

    with col2:
        # Copy to clipboard via JS
        escaped = final_blog.replace("`", "\\`").replace("$", "\\$")
        copy_js = f"""
        <button onclick="navigator.clipboard.writeText(`{escaped[:5000]}`).then(() => alert('Copied to clipboard!'))"
                style="width:100%; padding:0.5rem; background:#e94560; color:white; border:none; border-radius:6px; cursor:pointer; font-size:0.9rem;">
            📋 Copy Markdown
        </button>
        """
        st.markdown(copy_js, unsafe_allow_html=True)

    with col3:
        st.link_button(
            "📤 Open in Medium",
            "https://medium.com/new-story",
            use_container_width=True,
        )
