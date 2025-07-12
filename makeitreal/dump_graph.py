import typer

from .graph import IdeationWorkflow

app = typer.Typer(help="Dump workflow graph")


@app.command()
def dump() -> None:
    """Dump the AI workflow graph."""
    diagram = IdeationWorkflow().graph.get_graph().draw_mermaid()
    print(diagram)
