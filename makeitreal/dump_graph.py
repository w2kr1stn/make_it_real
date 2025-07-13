import typer

from .graph2 import IdeationWorkflow

app = typer.Typer(help="Dump workflow graph")


@app.command()
def dump() -> None:
    """Dump the AI workflow graph mermaid diagram."""
    print(IdeationWorkflow().graph.get_graph().draw_mermaid())
