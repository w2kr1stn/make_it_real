"""Context7 search tools for library documentation lookup."""

from langchain_core.tools import tool

from makeitreal.tools.mcp_client import search_library_documentation


@tool
async def search_library_docs(library_name: str, topic: str | None = None) -> str:
    """Search for up-to-date library documentation using Context7."""
    docs = await search_library_documentation(library_name, topic)
    topic_info = f" (focused on: {topic})" if topic else ""
    return (
        f"Library Documentation for {library_name}{topic_info}:\n\n{docs}"
        if docs
        else f"Library documentation not found for: {library_name}"
    )
