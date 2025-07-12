"""CLI interface for MakeItReal using Typer and Rich."""

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .llm import simple_llm_call

app = typer.Typer(help="Transform ideas into structured product concepts")
console = Console()


@app.command()
def idea(
    description: str = typer.Argument(..., help="Your product idea description"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Analyze and structure a product idea."""

    if verbose:
        console.print(f"[dim]Processing idea: {description}[/dim]")

    console.print(Panel("🧠 Analyzing your product idea...", style="blue"))

    try:
        with console.status("[green]Thinking...", spinner="dots"):
            result = simple_llm_call(description)

        console.print(Panel(Markdown(result), title="Product Analysis", style="green"))

    except Exception as e:
        console.print(Panel(f"❌ Error: {str(e)}", title="Error", style="red"))
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
