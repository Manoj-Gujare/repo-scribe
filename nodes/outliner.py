import json
import logging
from langchain_core.messages import HumanMessage
from models.state import RepoScribeState
from nodes.analyzer import get_llm

logger = logging.getLogger(__name__)


def generate_outline(state: RepoScribeState) -> RepoScribeState:
    """Generate structured blog outline using LLM."""
    if state.get("error"):
        return state

    logger.info("Generating blog outline...")
    state["current_step"] = "outlining"

    settings_info = f"Style: {state.get('blog_style', 'medium')}, Tone: {state.get('blog_tone', 'technical')}"

    prompt = f"""You are a technical blog writer creating an outline for a {state.get('blog_style', 'Medium')}-style post.

Repository: {state.get('repo_name', '')}
Purpose: {state.get('repo_analysis', '')}
Tech Stack: {', '.join(state.get('tech_stack', []))}
Architecture: {state.get('architecture_summary', '')}
{settings_info}

Create a compelling, SEO-friendly blog outline. Respond ONLY with valid JSON:
{{
  "title": "catchy SEO-friendly title",
  "subtitle": "descriptive subtitle",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "sections": [
    {{"name": "Introduction", "key_points": ["point 1", "point 2"]}},
    {{"name": "The Problem", "key_points": ["point 1", "point 2"]}},
    {{"name": "Tech Stack", "key_points": ["point 1", "point 2"]}},
    {{"name": "Architecture", "key_points": ["point 1", "point 2"]}},
    {{"name": "Code Walkthrough", "key_points": ["point 1", "point 2"]}},
    {{"name": "Results & Demo", "key_points": ["point 1", "point 2"]}},
    {{"name": "Conclusion", "key_points": ["point 1", "point 2"]}}
  ]
}}"""

    try:
        llm = get_llm()
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        state["blog_outline"] = json.loads(content)
    except Exception as e:
        logger.error(f"Outline generation failed: {e}")
        repo_name = state.get("repo_name", "Project")
        state["blog_outline"] = {
            "title": f"Building {repo_name}: A Technical Deep Dive",
            "subtitle": f"Exploring the architecture and implementation of {repo_name}",
            "tags": state.get("tech_stack", ["Python"])[:5],
            "sections": [
                {"name": "Introduction", "key_points": ["Overview", "Motivation"]},
                {"name": "The Problem", "key_points": ["Context", "Challenges"]},
                {"name": "Tech Stack", "key_points": ["Tools used"]},
                {"name": "Architecture", "key_points": ["System design"]},
                {"name": "Code Walkthrough", "key_points": ["Key code"]},
                {"name": "Results & Demo", "key_points": ["Output"]},
                {"name": "Conclusion", "key_points": ["Summary"]},
            ],
        }

    return state
