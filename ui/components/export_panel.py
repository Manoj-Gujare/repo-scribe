import streamlit as st


def render_export_panel(final_blog: str, repo_name: str):
    """Render export options for the generated blog."""
    st.subheader("Export")

    filename = f"{repo_name.replace('/', '-')}_blog.md" if repo_name else "blog.md"

    st.download_button(
        label="📥 Download .md",
        data=final_blog,
        file_name=filename,
        mime="text/markdown",
    )
