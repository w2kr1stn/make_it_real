"""CLI interface for aiask using Typer and Rich."""

import logging
import sys
from pathlib import Path

import typer
from pydantic import ValidationError
from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown

from .client import AIClient
from .config import get_settings
from .models import QuestionInput

app = typer.Typer(help="AI-powered question answering CLI")
console = Console()


def setup_logging() -> None:
    """Setup logging to file with rotation."""
    from logging.handlers import RotatingFileHandler

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Clear existing handlers
    logging.getLogger().handlers.clear()

    # Setup rotating file handler (5 files × 1MB each)
    handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5,
    )
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


@app.command()
def main(
    question: str = typer.Argument(..., help="Your question for the AI"),
    local: bool = typer.Option(False, "--local", help="Use LocalAI instead of OpenAI"),
) -> None:
    """Ask a question and get an AI-powered answer."""

    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Validate input
        validated_input = QuestionInput(message=question)
        logger.info(f"Question received: {len(validated_input.message)} chars")

        # Load settings
        settings = get_settings()

        # Initialize AI client
        client = AIClient(settings, use_local=local)

        # Show spinner while processing
        with console.status("[green]Thinking...", spinner="dots"):
            response = client.ask_question_with_retry(validated_input.message)

        # Display response with Rich formatting
        rprint("🤖 [green]Bot:[/green]")
        console.print(Markdown(response.content))

        # Log response details
        logger.info(f"Response: {response.tokens_used} tokens, {response.latency_ms}ms")

    except ValidationError as e:
        error_msg = e.errors()[0]["msg"]
        if "empty" in error_msg.lower() or "1000" in error_msg:
            rprint("❌ [red]Error: message must be 1-1000 characters[/red]")
        else:
            rprint(f"❌ [red]Error: {error_msg}[/red]")
        logger.error(f"Validation error: {error_msg}")
        sys.exit(1)

    except RuntimeError as e:
        if "Service busy" in str(e):
            rprint("❌ [yellow]Service busy, try later[/yellow]")
        else:
            rprint(f"❌ [red]Error: {e}[/red]")
        logger.error(f"Runtime error: {e}")
        sys.exit(1)

    except Exception as e:
        rprint(f"❌ [red]Unexpected error: {e}[/red]")
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()
