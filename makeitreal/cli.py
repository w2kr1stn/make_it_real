"""CLI interface for MakeItReal using Typer and Rich."""

import asyncio

import typer
from langgraph.types import Command
from rich.console import Console
from rich.panel import Panel

from makeitreal.graph import IdeationWorkflow

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

    while len(state.get("__interrupt__") or []) > 0:
        interrupts = state["__interrupt__"]
        proposal_key = interrupts[0].value["key"]
        state = interrupts[0].value["state"]
        proposal = state.get(proposal_key)
        print(
            f"{proposal_key}:"
            + "".join([f"\n  {i + 1}. {x}" for i, x in enumerate(proposal.proposed_items)])
        )

        approved = False
        while True:
            approval = input(f"Do you approve {proposal_key}? [Y|n]")
            approved = not approval or approval.lower() == "y"
            if approved or approval.lower() == "n":
                break
        change_request = ""
        if not approved:
            change_request = input("What do you want to change?")
        state = await workflow.graph.ainvoke(Command(resume=change_request), config)

    # Save final state after all interrupts are handled
    workflow._save_state_to_json(state)


if __name__ == "__main__":
    app()
