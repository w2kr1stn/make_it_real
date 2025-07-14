"""Web search tools for market research and competitor analysis."""

from langchain_core.tools import tool


@tool
def search_suitable_techstack(query: str) -> str:
    """Search for relevant technologies for a suitable tech stack
    to implement the defined features."

    Args:
        query: Search query for techstack research

    Returns:
        Formatted techstack research results
    """
    # For PoC, using a mock implementation
    mock_results = [
        "Python for backend development",
        "React for frontend development",
        "PostgreSQL for database management",
        "Docker for containerization",
        "Redis for caching",
        "FastAPI for building APIs",
    ]

    return f"Techstack research results for: {query}\n" + "\n".join(
        f"{i + 1}. {result}" for i, result in enumerate(mock_results)
    )
