import json
import logging
import boto3
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage
from config.settings import get_settings
from models.state import RepoScribeState

logger = logging.getLogger(__name__)


def get_llm():
    settings = get_settings()
    client = boto3.client(
        service_name="bedrock-runtime",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    return ChatBedrock(
        client=client,
        model_id=settings.BEDROCK_MODEL_ID,
        model_kwargs={"temperature": 0.7, "max_tokens": 4096},
    )


def analyze_repo(state: RepoScribeState) -> RepoScribeState:
    """Analyze repository structure using LLM."""
    if state.get("error"):
        return state

    logger.info("Analyzing repository structure...")
    state["current_step"] = "analysis"

    file_tree_str = "\n".join(state.get("file_tree", [])[:50])
    key_files_str = ""
    for fname, content in list(state.get("key_files", {}).items())[:3]:
        key_files_str += f"\n### {fname}\n```\n{content[:1500]}\n```\n"

    prompt = f"""You are analyzing a GitHub repository. Based on the information below, provide a structured JSON analysis.

Repository: {state.get('repo_name', '')}
Description: {state.get('repo_description', '')}
Languages: {', '.join(state.get('languages', []))}

README (excerpt):
{state.get('readme', '')[:2000]}

File Tree:
{file_tree_str}

Key Source Files:
{key_files_str}

Recent Commits:
{state.get('commits_summary', '')}

Respond ONLY with valid JSON in this exact format:
{{
  "purpose": "2-3 sentence description of what the project does",
  "tech_stack": ["list", "of", "tools", "frameworks", "libraries"],
  "architecture_summary": "how the system is structured and key components",
  "key_features": ["feature 1", "feature 2", "feature 3"],
  "novelty": "what makes this project interesting or unique"
}}"""

    try:
        llm = get_llm()
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()

        # Extract JSON if wrapped in code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        analysis = json.loads(content)
        state["repo_analysis"] = analysis.get("purpose", "")
        state["tech_stack"] = analysis.get("tech_stack", [])
        state["architecture_summary"] = analysis.get("architecture_summary", "")
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        state["repo_analysis"] = state.get("repo_description", "A software repository.")
        state["tech_stack"] = state.get("languages", [])
        state["architecture_summary"] = "Architecture details unavailable."

    return state
