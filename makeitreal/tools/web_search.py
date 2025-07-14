"""Web search tools for market research and competitor analysis."""

import asyncio
import re

import aiohttp
from bs4 import BeautifulSoup
from ddgs import DDGS
from langchain_core.tools import tool


async def _ddg_search(query: str) -> str:
    """Search for relevant technologies for a suitable tech stack
    and return result URLs"""
    with DDGS() as ddgs:
        return [r["href"] for r in list(ddgs.text(query, max_results=1))]


async def _fetch_url_content(session: aiohttp.ClientSession, url: str) -> str | None:
    """Fetch content from a URL."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status == 200:
                return await response.text()
    except Exception:
        pass
    return None


def _clean_html(html: str) -> str:
    """Clean HTML and extract text content."""
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted elements
    for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
        element.decompose()

    # Get text content
    text = soup.get_text()

    # Clean up whitespace
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    # Limit length
    return text[:2000] if len(text) > 2000 else text


async def _fetch_urls_parallel(urls: list[str]) -> list[str]:
    """Fetch multiple URLs in parallel."""
    async with aiohttp.ClientSession() as session:
        tasks = [_fetch_url_content(session, url) for url in urls]
        contents = await asyncio.gather(*tasks)
        return [_clean_html(content) for content in contents if content]


@tool
async def search_suitable_techstack(query: str) -> str:
    """Search for relevant technologies for a suitable tech stack
    to implement the defined features.

    Args:
        query: Search query for techstack research

    Returns:
        Formatted techstack research results
    """
    try:
        # Google search
        urls = await _ddg_search(query)

        if not urls:
            return f"No search results found for: {query}"

        # Fetch content from URLs in parallel
        contents = await _fetch_urls_parallel(urls)

        # Format results
        results = []
        for i, content in enumerate(contents):
            if content:
                results.append(f"Result {i + 1}: {content[:2000]}")

        if not results:
            return f"No accessible content found for: {query}"

        print(f"Techstack search results for: {query}\n" + "\n".join(results))
        return f"Techstack research results for: {query}\n\n" + "\n\n".join(results)

    except Exception as e:
        return f"Search failed for '{query}': {str(e)}"
