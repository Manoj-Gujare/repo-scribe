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
        if any(kw in section_name.lower() for kw in ["code", "walkthrough", "implementation", "deep dive"]):
            for fname, content in list(key_files.items())[:3]:
                code_context += f"\n```python\n# {fname}\n{content[:1500]}\n```\n"

        web_hint = ""
        if web_context and ("introduction" in section_name.lower() or "conclusion" in section_name.lower()):
            web_hint = f"\nRelated resources for context:\n{web_context[:500]}"

        section_guidance = {
            "Introduction": "Start with a strong hook (a relatable problem or surprising stat). Then briefly explain what this project is, what pain it solves, and end with a clear 'What you'll learn' bullet list.",
            "The Problem": "Paint the problem vividly. Use a concrete scenario or frustration a developer would recognize. Explain why naive or existing solutions don't cut it.",
            "Prerequisites": "List required tools, languages, and knowledge as a clean bullet list. Be specific about versions where it matters. Keep it brief.",
            "Tech Stack & Why": "For each major tool, give a short paragraph: what it is, why it was chosen over alternatives, and any caveats. Use a small table or bullet structure.",
            "Architecture Overview": "Describe the system at a high level. Explain how components interact and why the design was structured that way. Use a numbered flow or prose diagram description.",
            "Implementation Deep Dive": "Walk through the most important or non-obvious parts of the code. Explain *why* code was written the way it was, not just what it does. Use inline code references and snippets.",
            "Challenges & How We Solved Them": "Be honest about what was hard. Describe what was tried first, why it failed, and how the final solution was reached. This is often the most valuable section.",
            "Results & Demo": "Show what the finished project produces. Describe example input/output, performance numbers, or user-facing behavior concretely.",
            "Key Takeaways": "Write 4–6 punchy bullet points summarizing the most reusable lessons from this project. Each should be actionable or insightful on its own.",
            "Conclusion": "Briefly recap what was built and why it matters. Mention 2–3 future improvements. End with a direct call to action: star the repo, try it, contribute, or share.",
        }
        extra_guidance = section_guidance.get(section_name, "Write clear, well-structured content with examples where relevant.")

        prompt = f"""You are writing a {blog_tone} blog post in {state.get('blog_style', 'Medium')} style.

Blog title: {outline.get('title', '')}
Current section: **{section_name}**
Key points to cover: {', '.join(key_points)}

Repository context:
- Name: {state.get('repo_name', '')}
- Purpose: {state.get('repo_analysis', '')}
- Tech stack: {', '.join(state.get('tech_stack', []))}
- Architecture: {state.get('architecture_summary', '')}

Previously written sections (for narrative continuity):
{written_so_far[-1500:] if written_so_far else 'This is the first section.'}
{code_context}
{web_hint}

Section guidance: {extra_guidance}

Write the "{section_name}" section in approximately {words_per_section} words.
Use proper Markdown formatting:
- Use **bold** for key terms and important points
- Use bullet lists or numbered lists where appropriate
- Use `inline code` for all technical names, functions, and commands
- Use > blockquotes for tips, warnings, or notable callouts (e.g. > **Tip:** ...)
- Include code blocks with language tags when showing code
Do NOT include the section heading — just the content.
Tone: {blog_tone}. Write for a technical audience. Be specific, not generic."""

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
