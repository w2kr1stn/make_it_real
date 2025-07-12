"""CLI interface for MakeItReal using Typer and Rich."""

import asyncio

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .graph import IdeationWorkflow

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

    try:
        workflow = IdeationWorkflow()
        thread_id = "cli_session"  # Use consistent thread_id for checkpointing

        with console.status("[green]Workflow processing...", spinner="dots"):
            result = asyncio.run(workflow.run(description, thread_id))

        # Check if workflow was interrupted for human review
        # LangGraph interrupts return the current state before the interrupt node
        if result.get("evaluation_results") and result.get("current_phase") == "evaluated":
            console.print()
            console.print(
                Panel(
                    "🔍 Technical specification and evaluation completed!\n"
                    "The workflow is paused for your review.",
                    title="Human Review Required",
                    style="yellow",
                )
            )

            result = _handle_human_review(workflow, result, thread_id)

        # Handle rejection case
        if result.get("current_phase") == "rejected":
            console.print()
            console.print(
                Panel(
                    "The workflow was terminated because the specification was rejected.\n"
                    "You can run the command again to generate a new specification.",
                    title="Workflow Terminated",
                    style="red",
                )
            )
            return

        if result.get("error"):
            raise Exception(result["error"])

        curation = result["product_idea"]
        technical_spec = result.get("technical_spec", {})
        evaluation_results = result.get("evaluation_results", {})

        _display_structured_results(curation, technical_spec, evaluation_results)

    except Exception as e:
        console.print(Panel(f"❌ Error: {str(e)}", title="Error", style="red"))
        raise typer.Exit(1) from e


def _handle_human_review(workflow: IdeationWorkflow, current_result: dict, thread_id: str) -> dict:
    """Handle human review workflow interruption."""

    # Display current technical spec and evaluation for review
    technical_spec = current_result.get("technical_spec", {})
    evaluation_results = current_result.get("evaluation_results", {})

    if technical_spec:
        _display_review_summary(technical_spec, evaluation_results)

    console.print()

    # Get user decision
    while True:
        choice = (
            Prompt.ask("How would you like to proceed? (approve/changes/reject)", default="approve")
            .lower()
            .strip()
        )

        if choice in ["approve", "a", "1"]:
            decision = {"action": "approve"}
            break
        elif choice in ["request_changes", "changes", "change", "c", "2"]:
            feedback = Prompt.ask("What changes would you like to request?")
            decision = {"action": "request_changes", "feedback": feedback}
            break
        elif choice in ["reject", "r", "3"]:
            if Confirm.ask("Are you sure you want to reject this specification?"):
                decision = {"action": "reject"}
                break
            # Continue loop if user cancels rejection
        else:
            console.print("❌ Invalid choice. Please enter: approve, changes, or reject")

    # Resume workflow with user decision
    config = {"configurable": {"thread_id": thread_id}}

    try:
        console.print()

        # Handle rejection immediately without resuming workflow
        if decision.get("action") == "reject":
            console.print("❌ Specification rejected. Workflow terminated.")
            return {
                **current_result,
                "current_phase": "rejected",
                "error": "Technical specification rejected by user",
            }

        with console.status("[green]Processing your decision...", spinner="dots"):
            # Resume workflow by providing the interrupt response
            final_result = asyncio.run(workflow.graph.ainvoke(decision, config))

        return final_result

    except Exception as e:
        console.print(Panel(f"❌ Error resuming workflow: {str(e)}", style="red"))
        return current_result


def _display_review_summary(technical_spec: dict, evaluation_results: dict = None) -> None:
    """Display a summary of the technical specification and evaluation for review."""

    # Press Release
    press_release = technical_spec.get("press_release", {})
    if press_release.get("headline"):
        console.print(
            Panel(
                f"**{press_release.get('headline', 'N/A')}**\n\n"
                f"{press_release.get('intro', 'N/A')[:150]}...",
                title="📰 Press Release Preview",
                style="blue",
            )
        )

    # Quick stats
    user_stories = technical_spec.get("user_stories", [])
    tech_reqs = technical_spec.get("technical_requirements", [])

    stats_table = Table(title="📊 Specification Overview", show_header=False)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="yellow")

    stats_table.add_row("User Stories", str(len(user_stories)))
    stats_table.add_row("Technical Requirements", str(len(tech_reqs)))

    # Add evaluation results if available
    if evaluation_results:
        feasibility = evaluation_results.get("feasibility_score", 0)
        go_no_go = evaluation_results.get("go_no_go", "UNKNOWN")
        stats_table.add_row("Feasibility Score", f"{feasibility:.2f}/1.0")
        stats_table.add_row("Recommendation", go_no_go)

    console.print(stats_table)

    # Display evaluation details if available
    if evaluation_results:
        console.print()
        console.print(
            Panel(
                f"**Risk Assessment:** {evaluation_results.get('risk_assessment', 'N/A')}\n\n"
                f"**Go/No-Go:** {evaluation_results.get('go_no_go', 'UNKNOWN')}",
                title="🔍 Evaluation Results",
                style="green" if evaluation_results.get("go_no_go") == "GO" else "red",
            )
        )


def _display_structured_results(
    curation: dict, technical_spec: dict = None, evaluation_results: dict = None
) -> None:
    """Display structured curation results, technical specification, and evaluation using Rich."""

    console.print()
    # Product Idea Overview
    idea_table = Table(title="📝 Product Concept", show_header=False)
    idea_table.add_column("Field", style="cyan", width=20)
    idea_table.add_column("Value", style="white")

    product_idea = curation["product_idea"]
    idea_table.add_row("Problem", product_idea["problem_statement"])
    idea_table.add_row("Value Proposition", product_idea["value_proposition"])
    idea_table.add_row("Target Users", ", ".join(product_idea["target_users"]))

    console.print(idea_table)
    console.print()

    # Market Analysis
    market_table = Table(title="📊 Market Analysis", show_header=False)
    market_table.add_column("Aspect", style="yellow", width=20)
    market_table.add_column("Assessment", style="white")

    market = curation["market_analysis"]
    market_table.add_row("Market Size", market["market_size"])

    # Competitors
    if market["competitors"]:
        competitors_list = []
        for comp in market["competitors"]:
            if isinstance(comp, dict) and "name" in comp and "description" in comp:
                competitors_list.append(f"{comp['name']}: {comp['description']}")
            elif isinstance(comp, str):
                competitors_list.append(comp)
            else:
                competitors_list.append(str(comp))

        if competitors_list:
            market_table.add_row("Key Competitors", "\n".join(competitors_list))

    console.print(market_table)
    console.print()

    # Opportunities & Risks
    opp_risk_table = Table(title="⚖️ Opportunities & Risks")
    opp_risk_table.add_column("🟢 Opportunities", style="green")
    opp_risk_table.add_column("🔴 Risks", style="red")

    opportunities = market.get("opportunities", [])
    risks = market.get("risks", [])

    # Ensure they are lists
    if not isinstance(opportunities, list):
        opportunities = []
    if not isinstance(risks, list):
        risks = []

    max_rows = max(len(opportunities), len(risks)) if opportunities or risks else 0

    for i in range(max_rows):
        opp = opportunities[i] if i < len(opportunities) else ""
        risk = risks[i] if i < len(risks) else ""
        opp_risk_table.add_row(opp, risk)

    console.print(opp_risk_table)
    console.print()

    # Recommended Features
    features = curation.get("recommended_features", [])
    if isinstance(features, list) and features:
        features_panel = Panel(
            "\n".join([f"• {feature}" for feature in features]),
            title="🚀 Recommended Features",
            style="blue",
        )
        console.print(features_panel)
        console.print()

    # Next Steps
    next_steps = curation.get("next_steps", [])
    if isinstance(next_steps, list) and next_steps:
        steps_panel = Panel(
            "\n".join([f"{i + 1}. {step}" for i, step in enumerate(next_steps)]),
            title="📋 Next Steps",
            style="magenta",
        )
        console.print(steps_panel)

    # Technical Specification (if available)
    if technical_spec:
        console.print()
        console.print(Panel("📋 Technical Specification Generated", style="cyan"))

        # Press Release
        press_release = technical_spec.get("press_release", {})
        if press_release.get("headline"):
            pr_panel = Panel(
                f"**{press_release.get('headline', 'N/A')}**\n\n"
                f"{press_release.get('intro', 'N/A')}\n\n"
                f"*Problem:* {press_release.get('problem', 'N/A')}\n"
                f"*Solution:* {press_release.get('solution', 'N/A')}",
                title="📰 Press Release Preview",
                style="green",
            )
            console.print(pr_panel)
            console.print()

        # User Stories
        user_stories = technical_spec.get("user_stories", [])
        if user_stories:
            stories_table = Table(title="📋 User Stories", show_header=True)
            stories_table.add_column("Story", style="cyan")
            stories_table.add_column("Priority", style="yellow")

            for story in user_stories[:5]:  # Show first 5 stories
                title = story.get("title", "N/A")
                priority = story.get("priority", "medium")
                stories_table.add_row(title, priority.upper())

            console.print(stories_table)
            console.print()

        # Technical Requirements
        tech_reqs = technical_spec.get("technical_requirements", [])
        if tech_reqs:
            tech_panel = Panel(
                "\n".join([f"• {req}" for req in tech_reqs[:8]]),  # Show first 8
                title="⚙️ Technical Requirements",
                style="blue",
            )
            console.print(tech_panel)
            console.print()

        # Timeline
        timeline = technical_spec.get("timeline", "")
        if timeline:
            timeline_panel = Panel(timeline, title="⏱️ Development Timeline", style="magenta")
            console.print(timeline_panel)
            console.print()

    # Evaluation Results (if available)
    if evaluation_results:
        console.print()

        # Evaluation scores
        eval_table = Table(title="📊 Feasibility Evaluation", show_header=False)
        eval_table.add_column("Metric", style="cyan", width=20)
        eval_table.add_column("Score", style="yellow")

        eval_table.add_row(
            "Technical Feasibility", f"{evaluation_results.get('feasibility_score', 0):.2f}/1.0"
        )
        eval_table.add_row(
            "Resource Requirements", f"{evaluation_results.get('resource_score', 0):.2f}/1.0"
        )
        eval_table.add_row(
            "Timeline Realism", f"{evaluation_results.get('timeline_score', 0):.2f}/1.0"
        )

        console.print(eval_table)
        console.print()

        # Risk assessment and recommendation
        go_no_go = evaluation_results.get("go_no_go", "UNKNOWN")
        risk_assessment = evaluation_results.get("risk_assessment", "No assessment available")

        eval_panel = Panel(
            f"**Risk Assessment:**\n{risk_assessment}\n\n**Final Recommendation:** {go_no_go}",
            title="🔍 Evaluation Summary",
            style="green" if go_no_go == "GO" else "red",
        )
        console.print(eval_panel)

        # Recommendations
        recommendations = evaluation_results.get("recommendations", [])
        if recommendations:
            console.print()
            rec_panel = Panel(
                "\n".join([f"• {rec}" for rec in recommendations[:5]]),  # Show first 5
                title="💡 Recommendations",
                style="blue",
            )
            console.print(rec_panel)


if __name__ == "__main__":
    app()
