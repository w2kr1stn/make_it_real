import typer
import asyncio
from .graph2 import IdeationWorkflow

app = typer.Typer(help="Dump workflow graph")


@app.command()
def dump() -> None:
    """Dump the AI workflow graph mermaid diagram."""
    workflow = IdeationWorkflow()
    asyncio.run(_dump(workflow))

async def _dump(workflow:IdeationWorkflow) -> None:
    """Dump the AI workflow graph mermaid diagram."""
    await workflow.ainit()
    print(workflow.graph.get_graph().draw_mermaid())