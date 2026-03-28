import logging
from langchain_core.messages import HumanMessage
from models.state import RepoScribeState
from nodes.analyzer import get_llm
from config.settings import get_settings

logger = logging.getLogger(__name__)


def write_blog(state: RepoScribeState) -> RepoScribeState:
    """Write each blog section using LLM with narrative continuity."""
    if state.get("error"):
        return state

    logger.info("Writing blog sections...")
    state["current_step"] = "writing"

    settings = get_settings()
    outline = state.get("blog_outline", {})
    sections_list = outline.get("sections", [])
    key_files = state.get("key_files", {})
    web_context = state.get("web_context", "")
    blog_tone = state.get("blog_tone", "technical")
    max_words = state.get("max_words") or settings.MAX_BLOG_WORDS

    llm = get_llm()
    blog_sections = {}
    written_so_far = ""

    words_per_section = max_words // max(len(sections_list), 1)

    for section in sections_list:
        section_name = section.get("name", "Section")
        key_points = section.get("key_points", [])

        code_context = ""
        if "code" in section_name.lower() or "walkthrough" in section_name.lower():
            for fname, content in list(key_files.items())[:2]:
                code_context += f"\n```python\n# {fname}\n{content[:1500]}\n```\n"

        web_hint = ""
        if web_context and ("introduction" in section_name.lower() or "conclusion" in section_name.lower()):
            web_hint = f"\nRelated resources for context:\n{web_context[:500]}"

        prompt = f"""You are writing a {blog_tone} blog post in {state.get('blog_style', 'Medium')} style.

Blog title: {outline.get('title', '')}
Current section: {section_name}
Key points to cover: {', '.join(key_points)}

Repository context:
- Name: {state.get('repo_name', '')}
- Purpose: {state.get('repo_analysis', '')}
- Tech stack: {', '.join(state.get('tech_stack', []))}
- Architecture: {state.get('architecture_summary', '')}

Previously written sections (for narrative continuity):
{written_so_far[-1000:] if written_so_far else 'This is the first section.'}
{code_context}
{web_hint}

Write the "{section_name}" section in approximately {words_per_section} words.
Use proper Markdown formatting. Do NOT include the section heading — just the content.
Tone: {blog_tone}. Write for a technical audience."""

        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            section_content = response.content.strip()
            blog_sections[section_name] = section_content
            written_so_far += f"\n\n## {section_name}\n{section_content}"
        except Exception as e:
            logger.error(f"Failed to write section '{section_name}': {e}")
            blog_sections[section_name] = f"*Content for {section_name} unavailable.*"

    state["blog_sections"] = blog_sections
    return state
