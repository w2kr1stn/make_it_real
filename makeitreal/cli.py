"""CLI interface for MakeItReal using Typer and Rich."""

import asyncio

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .agents import IdeaCurator

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
        with console.status("[green]Agent analyzing...", spinner="dots"):
            curator = IdeaCurator()
            result = asyncio.run(curator.process({"idea": description}))
            curation = result["curation_result"]

        _display_structured_results(curation)

    except Exception as e:
        console.print(Panel(f"❌ Error: {str(e)}", title="Error", style="red"))
        raise typer.Exit(1) from e


def _display_structured_results(curation: dict) -> None:
    """Display structured curation results using Rich tables and panels."""

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


if __name__ == "__main__":
    app()
