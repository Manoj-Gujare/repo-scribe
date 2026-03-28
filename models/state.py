from typing import TypedDict, Optional, List, Dict


class RepoScribeState(TypedDict):
    # Input
    github_url: str
    blog_style: str
    blog_tone: str

    # Ingestion outputs
    repo_name: str
    repo_description: str
    readme: str
    file_tree: List[str]
    key_files: Dict[str, str]
    commits_summary: str
    languages: List[str]

    # Analysis outputs
    repo_analysis: str
    tech_stack: List[str]
    architecture_summary: str

    # Web search outputs
    web_context: Optional[str]

    # Blog generation outputs
    blog_outline: Dict
    blog_sections: Dict[str, str]

    # Final output
    final_blog: str
    metadata: Dict

    # Pipeline control
    tavily_enabled: bool
    max_words: int
    current_step: str
    error: Optional[str]
