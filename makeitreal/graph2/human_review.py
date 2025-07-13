"""Human review checkpoint for workflow interruption."""

from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.types import interrupt
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from .state import WorkflowState

console = Console()

async def human_review_node(state: WorkflowState) -> dict[str, Any]:
    features = state.get("features",[])
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
    action = decision.get("action", "").lower()

    return state


async def human_review_techstack_node(state: WorkflowState) -> dict[str, Any]:
    techStack = state.get("techStack",[])
    console.print(Panel("Reviewing techStack \n" + "\n".join(techStack)))
    return state
