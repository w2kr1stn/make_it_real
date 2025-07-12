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
    """Human review checkpoint for technical specification approval.

    This node interrupts the workflow to allow human review of the generated
    technical specification. The user can approve, request changes, or reject.

    Args:
        state: Current workflow state containing technical_spec

    Returns:
        Updated state dict with review decision and feedback
    """
    technical_spec = state.get("technical_spec", {})

    if not technical_spec:
        return {
            "error": "No technical specification available for review",
            "current_phase": "error",
        }

    # Display specification preview for review
    _display_spec_preview(technical_spec)

    # Interrupt workflow for human input
    decision = interrupt(
        {
            "type": "review_request",
            "message": "Please review the technical specification",
            "spec_preview": _get_spec_summary(technical_spec),
            "options": ["approve", "request_changes", "reject"],
        }
    )

    # Process user decision
    action = decision.get("action", "").lower()

    if action == "approve":
        console.print("✅ Specification approved. Continuing workflow...")
        return {
            "current_phase": "approved",
            "requires_human_review": False,
        }

    elif action == "request_changes":
        feedback = decision.get("feedback", "")
        if not feedback:
            feedback = Prompt.ask("What changes are needed?")

        console.print(f"🔄 Changes requested: {feedback}")

        # Add feedback message to trigger spec_writer revision
        feedback_message = HumanMessage(
            content=f"Please revise the specification based on this feedback: {feedback}"
        )

        return {
            "messages": [feedback_message],
            "current_phase": "revision_requested",
            "requires_human_review": True,
        }

    elif action == "reject":
        console.print("❌ Specification rejected.")
        return {
            "current_phase": "rejected",
            "error": "Technical specification rejected by user",
        }

    else:
        return {
            "error": f"Invalid review action: {action}",
            "current_phase": "error",
        }


def _display_spec_preview(technical_spec: dict) -> None:
    """Display technical specification preview for user review."""

    # Press Release section
    press_release = technical_spec.get("press_release", {})
    if press_release:
        headline = press_release.get("headline", "No headline")
        intro = press_release.get("intro", "No introduction")

        pr_content = f"**{headline}**\n\n{intro[:200]}..."
        console.print(Panel(pr_content, title="📰 Press Release", style="blue"))

    # User Stories preview
    user_stories = technical_spec.get("user_stories", [])
    if user_stories:
        stories_preview = "\n".join(
            [f"• {story.get('title', 'Untitled story')}" for story in user_stories[:3]]
        )
        if len(user_stories) > 3:
            stories_preview += f"\n... and {len(user_stories) - 3} more stories"

        console.print(Panel(stories_preview, title="📋 User Stories Preview", style="cyan"))

    # Technical Requirements
    tech_reqs = technical_spec.get("technical_requirements", [])
    if tech_reqs:
        reqs_preview = "\n".join([f"• {req}" for req in tech_reqs[:3]])
        if len(tech_reqs) > 3:
            reqs_preview += f"\n... and {len(tech_reqs) - 3} more requirements"

        console.print(Panel(reqs_preview, title="⚙️ Technical Requirements", style="yellow"))


def _get_spec_summary(technical_spec: dict) -> str:
    """Generate a concise summary of the technical specification."""
    press_release = technical_spec.get("press_release", {})
    user_stories = technical_spec.get("user_stories", [])
    tech_reqs = technical_spec.get("technical_requirements", [])

    summary_parts = []

    if press_release.get("headline"):
        summary_parts.append(f"Product: {press_release['headline']}")

    if user_stories:
        summary_parts.append(f"User Stories: {len(user_stories)} defined")

    if tech_reqs:
        summary_parts.append(f"Technical Requirements: {len(tech_reqs)} specified")

    return " | ".join(summary_parts) if summary_parts else "Specification generated"
