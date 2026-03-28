from github import Github
from github.GithubException import GithubException
from config.settings import get_settings


def get_github_client() -> Github:
    settings = get_settings()
    return Github(settings.GITHUB_TOKEN)


def fetch_repo_data(github_url: str) -> dict:
    """Fetch repository data from GitHub API."""
    client = get_github_client()

    # Normalize and parse owner/repo from URL
    normalized = github_url.strip().rstrip("/").removesuffix(".git")
    parts = normalized.replace("https://github.com/", "").split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise ValueError(f"Invalid GitHub URL: {github_url}")
    repo_path = f"{parts[0]}/{parts[1]}"

    try:
        repo = client.get_repo(repo_path)
    except GithubException as e:
        raise RuntimeError(f"Failed to fetch repo {repo_path}: {e}")

    # Metadata
    name = repo.name
    description = repo.description or ""
    languages = list(repo.get_languages().keys())

    # README
    try:
        readme_content = repo.get_readme().decoded_content.decode("utf-8")
    except Exception:
        readme_content = ""

    # File tree (up to 2 levels deep)
    file_tree = []
    try:
        contents = repo.get_contents("")
        while contents:
            item = contents.pop(0)
            file_tree.append(item.path)
            if item.type == "dir" and item.path.count("/") < 1:
                try:
                    contents.extend(repo.get_contents(item.path))
                except Exception:
                    pass
    except Exception:
        pass

    # Key source files (up to 5)
    priority_extensions = [".py", ".js", ".ts", ".go", ".java", ".rs", ".cpp"]
    priority_names = ["main", "app", "index", "core", "server", "api", "config"]
    key_files = {}

    all_files = [f for f in file_tree if any(f.endswith(ext) for ext in priority_extensions)]
    # Sort by priority
    def file_priority(path):
        name = path.split("/")[-1].split(".")[0].lower()
        return (0 if any(n in name for n in priority_names) else 1, len(path))

    all_files.sort(key=file_priority)

    for file_path in all_files[:5]:
        try:
            content = repo.get_contents(file_path)
            decoded = content.decoded_content.decode("utf-8", errors="replace")
            key_files[file_path] = decoded[:3000]  # limit size
        except Exception:
            pass

    # Last 10 commits
    commits_summary = ""
    try:
        commits = list(repo.get_commits()[:10])
        commit_lines = [f"- {c.commit.message.splitlines()[0]}" for c in commits]
        commits_summary = "\n".join(commit_lines)
    except Exception:
        pass

    return {
        "repo_name": name,
        "repo_description": description,
        "readme": readme_content,
        "file_tree": file_tree,
        "key_files": key_files,
        "commits_summary": commits_summary,
        "languages": languages,
    }
