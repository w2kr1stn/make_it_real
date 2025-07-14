import asyncio

import typer

from makeitreal.agents.requirements_generator_agent import RequirementsGeneratorAgent
from makeitreal.agents.requirements_review_agent import RequirementsReviewAgent
from makeitreal.graph import IdeationWorkflow

app = typer.Typer(help="Dump workflow graph")


async def _dump(workflow: IdeationWorkflow) -> None:
    """Dump the AI workflow graph mermaid diagram."""
    await workflow.ainit()

    print("Main Graph (top-level; each node is actually a sub graph):")
    print("```mermaid")
    print(workflow.graph.get_graph().draw_mermaid())
    print("```")
    print(
        "Sub graph (used within each `requirements_analysis`, `techstack_discovery`, "
        "`task_creation` in the graph above)"
    )
    print("```mermaid")
    print(
        (
            await workflow._build_proposal_graph(
                key="features",
                generator_agent=RequirementsGeneratorAgent(),
                review_agent=RequirementsReviewAgent(),
            )
        )
        .get_graph()
        .draw_mermaid()
    )
    print("```")


@app.command()
def dump() -> None:
    """Dump the AI workflow graph mermaid diagram."""
    workflow = IdeationWorkflow()
    asyncio.run(_dump(workflow))
