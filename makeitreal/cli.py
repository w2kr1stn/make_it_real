"""CLI interface for MakeItReal using Typer and Rich."""

import asyncio

import typer
from rich.console import Console
from rich.panel import Panel
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
        with console.status("[green]Workflow processing...", spinner="dots"):
            workflow = IdeationWorkflow()
            result = asyncio.run(workflow.run(description))

            if result.get("error"):
                raise Exception(result["error"])

            curation = result["product_idea"]
            technical_spec = result.get("technical_spec", {})

        _display_structured_results(curation, technical_spec)

    except Exception as e:
        console.print(Panel(f"❌ Error: {str(e)}", title="Error", style="red"))
        raise typer.Exit(1) from e


def _display_structured_results(curation: dict, technical_spec: dict = None) -> None:
    """Display structured curation results and technical specification using Rich."""

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


if __name__ == "__main__":
    app()
