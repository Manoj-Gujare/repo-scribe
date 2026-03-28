import streamlit as st

PIPELINE_STEPS = [
    ("ingestion", "🔍 Fetching repository"),
    ("analysis", "🧠 Analyzing code structure"),
    ("web_search", "🌐 Searching the web"),
    ("outlining", "📋 Generating blog outline"),
    ("writing", "✍️  Writing blog sections"),
    ("formatting", "🎨 Formatting output"),
    ("done", None),  # Terminal state
]

STEP_ORDER = [s[0] for s in PIPELINE_STEPS]


def get_step_status(current_step: str, step_key: str, tavily_enabled: bool) -> str:
    """Determine the display status of a step."""
    if step_key == "web_search" and not tavily_enabled:
        return "skipped"

    if step_key == "done":
        return "done"

    try:
        current_idx = STEP_ORDER.index(current_step)
        step_idx = STEP_ORDER.index(step_key)
    except ValueError:
        return "pending"

    if step_idx < current_idx:
        return "done"
    elif step_idx == current_idx:
        return "running"
    else:
        return "pending"


def render_progress_tracker(current_step: str, tavily_enabled: bool, error: str = None):
    """Render the live pipeline progress tracker."""
    st.subheader("Pipeline Progress")

    for step_key, label in PIPELINE_STEPS:
        if label is None:
            continue

        status = get_step_status(current_step, step_key, tavily_enabled)

        if error and status == "running":
            status = "failed"

        icons = {
            "pending": "⬜",
            "running": "⏳",
            "done": "✅",
            "skipped": "⏭️",
            "failed": "❌",
        }

        icon = icons.get(status, "⬜")
        css_class = f"step-{status}"

        st.markdown(
            f'<div class="step-container {css_class}">{icon} {label}</div>',
            unsafe_allow_html=True,
        )

    if error:
        with st.expander("❌ Error Details", expanded=True):
            st.error(error)
