"""MCP Client wrapper for Context7 communication."""

import json
from typing import Any

import aiohttp


class MCPClient:
    """Async MCP Client for Context7 communication via Docker container."""

    def __init__(self, container_name: str = "context7-mcp"):
        """Initialize MCP client."""
        self.container_name = container_name
        self.session: aiohttp.ClientSession | None = None
        self.base_url = f"http://{container_name}:8080/mcp"
        self.request_id = 0

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self) -> None:
        """Connect to the Context7 MCP server via HTTP."""
        self.session = aiohttp.ClientSession()

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _send_request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Send a JSON-RPC request to the MCP server via HTTP."""
        if not self.session:
            raise RuntimeError("MCP client not connected")

        self.request_id += 1
        request = {"jsonrpc": "2.0", "id": self.request_id, "method": method, "params": params}

        async with self.session.post(
            self.base_url,
            json=request,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        ) as response:
            if response.status != 200:
                raise RuntimeError(f"HTTP error: {response.status}")

            # Parse SSE format: "event: message\ndata: {json}"
            response_text = await response.text()
            for line in response_text.strip().split("\n"):
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if "error" in data:
                        raise RuntimeError(f"MCP server error: {data['error']}")
                    return data.get("result", {})

    async def resolve_library_id(self, library_name: str) -> str | None:
        """Resolve a library name to Context7-compatible library ID."""
        result = await self._send_request(
            "tools/call", {"name": "resolve-library-id", "arguments": {"libraryName": library_name}}
        )

        # Extract first library ID from response text
        if isinstance(result, dict) and "content" in result and result["content"]:
            text = result["content"][0].get("text", "")
            for line in text.split("\n"):
                if "Context7-compatible library ID:" in line:
                    return line.split("Context7-compatible library ID:")[1].strip()
        return None

    async def get_library_docs(
        self, library_id: str, topic: str | None = None, tokens: int = 10000
    ) -> str | None:
        """Get documentation for a library."""
        arguments = {"context7CompatibleLibraryID": library_id, "tokens": tokens}
        if topic:
            arguments["topic"] = topic

        result = await self._send_request(
            "tools/call", {"name": "get-library-docs", "arguments": arguments}
        )

        # Extract documentation text from response
        if isinstance(result, dict) and "content" in result and result["content"]:
            return result["content"][0].get("text", "")
        return None


async def search_library_documentation(library_name: str, topic: str | None = None) -> str | None:
    """Search for library documentation using Context7 MCP."""
    async with MCPClient() as client:
        library_id = await client.resolve_library_id(library_name)
        if library_id:
            return await client.get_library_docs(library_id, topic)
        return None
