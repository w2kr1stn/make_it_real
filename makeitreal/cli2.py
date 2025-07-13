"""CLI interface for MakeItReal using Typer and Rich."""

import asyncio

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from random import randint
from langgraph.types import Command, interrupt

from .graph2 import IdeationWorkflow

app = typer.Typer(help="Transform ideas into structured product concepts")
console = Console()


@app.command()
def idea(
    description: str = typer.Argument(..., help="Your product idea description"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """Analyze and structure a product idea using the IdeaCurator agent."""

    if verbose:
        console.print(f"[dim]Processing idea: {description}[/dim]")

    console.print(Panel("🧠 Analyzing your product idea...", style="blue"))

    asyncio.run(_run_idea(description, verbose))


async def _run_idea(description: str, verbose: bool):
    workflow = IdeationWorkflow()
    await workflow.ainit()

    thread_id = "cli_session"
    config = {"configurable": {"thread_id": thread_id}}

    with console.status("[green]Workflow processing...", spinner="dots"):
        state = await workflow.run(description, thread_id)

    while len(state.get('__interrupt__') or []) > 0:
        interrupts = state['__interrupt__']
        proposal_key = interrupts[0].value['key']
        state = interrupts[0].value['state']
        proposal = state.get(proposal_key)
        print(f"{proposal_key}:\n- "+"\n- ".join(proposal.proposedItems))

        approved = False
        while True:
            approval = input(f"Do you approve {proposal_key}? [Y|n]")
            approved = not approval or approval.lower() == "y"
            if approved or approval.lower() == "n":
                break
        changeRequest = ''
        if not approved:
            changeRequest = input(f"What do you want to change?")
        state = asyncio.run(workflow.graph.ainvoke(Command(resume=changeRequest), config))

if __name__ == "__main__":
    app()