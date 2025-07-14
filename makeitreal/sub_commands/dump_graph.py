import asyncio

import typer

from makeitreal.graph import IdeationWorkflow

app = typer.Typer(help="Dump workflow graph")


async def _dump(workflow: IdeationWorkflow) -> None:
    """Dump the AI workflow graph mermaid diagram."""
    await workflow.ainit()
    print(workflow.graph.get_graph().draw_mermaid())


@app.command()
def dump() -> None:
    """Dump the AI workflow graph mermaid diagram."""
    workflow = IdeationWorkflow()
    asyncio.run(_dump(workflow))
