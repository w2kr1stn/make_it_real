"""Human review checkpoint for workflow interruption."""

from typing import Any

from langgraph.types import interrupt
from rich.console import Console
from rich.panel import Panel

from makeitreal.graph.state import WorkflowState

console = Console()


async def human_review_node(state: WorkflowState) -> dict[str, Any]:
    features = state.get("features", [])
    console.print(Panel("Reviewing features \n" + "\n".join(features)))

    decision = interrupt(
        {
            "type": "review_request",
            "message": "Please review the technical specification",
            "spec_preview": "preview",
            "options": ["approve", "request_changes", "reject"],
        }
    )

    # Process user decision
    decision.get("action", "").lower()

    return state


async def human_review_techstack_node(state: WorkflowState) -> dict[str, Any]:
    tech_stack = state.get("tech_stack", [])
    console.print(Panel("Reviewing tech_stack \n" + "\n".join(tech_stack)))
    return state
