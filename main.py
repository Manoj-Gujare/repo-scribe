import subprocess
import sys
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer(
    name="repo-scribe",
    help="Generate publication-ready technical blog posts from GitHub repositories.",
    add_completion=False,
)
console = Console()


@app.command()
def generate(
    url: str = typer.Option(..., "--url", "-u", help="GitHub repository URL"),
    style: str = typer.Option("medium", "--style", "-s", help="Blog style: medium | towardsdatascience"),
    tone: str = typer.Option("technical", "--tone", "-t", help="Blog tone: technical | intermediate | beginner-friendly"),
    max_words: int = typer.Option(1500, "--max-words", "-w", help="Maximum word count"),
    no_web_search: bool = typer.Option(False, "--no-web-search", help="Disable Tavily web search"),
):
    """Generate a technical blog post from a GitHub repository."""
    from graph.pipeline import run_pipeline
    from config.settings import get_settings

    console.print(Panel.fit(
        f"[bold]repo-scribe[/bold]\n[dim]Generating blog for:[/dim] {url}",
        border_style="blue",
    ))

    settings = get_settings()
    tavily_enabled = bool(settings.TAVILY_API_KEY) and not no_web_search

    if tavily_enabled:
        console.print("[green]🟢 Web search enabled[/green]")
    else:
        console.print("[yellow]🔴 Web search disabled[/yellow]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running pipeline...", total=None)

        try:
            result = run_pipeline(
                github_url=url,
                blog_style=style,
                blog_tone=tone,
                tavily_enabled=tavily_enabled,
            )
        except Exception as e:
            progress.stop()
            console.print(f"[red]Pipeline failed: {e}[/red]")
            raise typer.Exit(1)

    if result.get("error"):
        console.print(f"[red]Error: {result['error']}[/red]")
        raise typer.Exit(1)

    metadata = result.get("metadata", {})
    word_count = metadata.get("word_count", 0)
    read_time = metadata.get("read_time", 0)
    repo_name = result.get("repo_name", "blog").replace("/", "-")
    output_path = f"output/{repo_name}_blog.md"

    console.print("\n[bold green]✅ Blog generated successfully[/bold green]")
    console.print(f"[blue]📝 Word count:[/blue] {word_count:,}")
    console.print(f"[blue]📖 Estimated read time:[/blue] {read_time} min")
    console.print(f"[blue]💾 Saved to:[/blue] {output_path}")


@app.command("run-ui")
def run_ui():
    """Launch the Streamlit web UI."""
    console.print("[bold]Launching repo-scribe UI...[/bold]")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)


if __name__ == "__main__":
    app()
