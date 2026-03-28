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

Create a compelling, SEO-friendly blog outline with rich sections that make for a genuinely useful technical article.
Respond ONLY with valid JSON:
{{
  "title": "catchy SEO-friendly title (action-oriented, explains the value)",
  "subtitle": "descriptive subtitle that explains what the reader will gain",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "sections": [
    {{"name": "Introduction", "key_points": ["hook sentence about the problem", "what this project does", "what the reader will learn"]}},
    {{"name": "The Problem", "key_points": ["specific pain point being solved", "why existing solutions fall short", "real-world impact"]}},
    {{"name": "Prerequisites", "key_points": ["required knowledge", "tools to install", "assumed background"]}},
    {{"name": "Tech Stack & Why", "key_points": ["each major tool/library chosen", "why each was chosen over alternatives", "version or notable constraints"]}},
    {{"name": "Architecture Overview", "key_points": ["high-level system design", "component responsibilities", "data flow"]}},
    {{"name": "Implementation Deep Dive", "key_points": ["most important code paths", "key design decisions", "non-obvious implementation details"]}},
    {{"name": "Challenges & How We Solved Them", "key_points": ["main technical challenge", "what was tried and failed", "final solution"]}},
    {{"name": "Results & Demo", "key_points": ["what the finished project does", "performance or quality metrics", "example output or screenshot description"]}},
    {{"name": "Key Takeaways", "key_points": ["main lesson 1", "main lesson 2", "what to reuse in other projects"]}},
    {{"name": "Conclusion", "key_points": ["summary of what was built", "next steps or future improvements", "call to action (star, fork, contribute)"]}}
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
                {"name": "Introduction", "key_points": ["Overview", "Motivation", "What you'll learn"]},
                {"name": "The Problem", "key_points": ["Context", "Challenges"]},
                {"name": "Prerequisites", "key_points": ["Required tools", "Assumed knowledge"]},
                {"name": "Tech Stack & Why", "key_points": ["Tools used", "Why chosen"]},
                {"name": "Architecture Overview", "key_points": ["System design", "Data flow"]},
                {"name": "Implementation Deep Dive", "key_points": ["Key code", "Design decisions"]},
                {"name": "Challenges & How We Solved Them", "key_points": ["Main hurdles", "Solutions"]},
                {"name": "Results & Demo", "key_points": ["Output", "Metrics"]},
                {"name": "Key Takeaways", "key_points": ["Lessons learned"]},
                {"name": "Conclusion", "key_points": ["Summary", "Next steps"]},
            ],
        }

    return state
