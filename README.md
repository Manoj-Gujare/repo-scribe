# 📝 repo-scribe

> Turn any GitHub repository into a publication-ready technical blog post — powered by LangGraph, AWS Bedrock, and Streamlit.

## Architecture

```
GitHub URL
    │
    ▼
┌─────────────────────────────────────────────────────┐
│                  LangGraph Pipeline                  │
│                                                     │
│  ingest_repo → analyze_repo → [web_search_context]  │
│                                        │            │
│                               generate_outline      │
│                                        │            │
│                                  write_blog         │
│                                        │            │
│                                 format_output       │
└─────────────────────────────────────────────────────┘
    │
    ▼
output/{repo_name}_blog.md
    │
    ▼
Streamlit UI (preview + download)
```

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/your-username/repo-scribe.git
cd repo-scribe
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required:
- `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` + `AWS_REGION` — AWS credentials with Bedrock access
- `GITHUB_TOKEN` — GitHub personal access token (for API rate limits)

Optional:
- `TAVILY_API_KEY` — enables web search enrichment

### 3. Run

**Streamlit UI:**
```bash
streamlit run app.py
# or
python main.py run-ui
```

**CLI:**
```bash
python main.py generate --url https://github.com/owner/repo
python main.py generate --url https://github.com/owner/repo --style towardsdatascience --tone beginner-friendly
python main.py generate --url https://github.com/owner/repo --max-words 2000
```

## Pipeline Steps

| Step | Node | Description |
|------|------|-------------|
| 1 | `ingest_repo` | Fetch README, file tree, source files, commits via GitHub API |
| 2 | `analyze_repo` | LLM-powered repo summarization (purpose, tech stack, architecture) |
| 3 | `web_search_context` | Tavily search enrichment *(optional)* |
| 4 | `generate_outline` | Create structured blog outline (title, sections, tags) |
| 5 | `write_blog` | Write each section with narrative continuity |
| 6 | `format_output` | Assemble final Markdown + YAML frontmatter + save |

## Environment Variables

See [`.env.example`](.env.example) for full reference.

## Tech Stack

- **LangGraph** — pipeline orchestration
- **LangChain + AWS Bedrock** — LLM calls (Claude 3.5 Sonnet)
- **PyGithub** — GitHub API
- **Tavily** — web search enrichment
- **Streamlit** — web UI
- **Typer + Rich** — CLI

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes
4. Open a pull request

---

*Built with LangGraph · LangChain · AWS Bedrock · Streamlit*
