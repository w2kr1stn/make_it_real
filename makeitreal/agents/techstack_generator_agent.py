"""tech stack generator agent."""

from typing import Any

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from makeitreal.agents.requirements_generator_agent import RequirementsGeneratorAgent
from makeitreal.config import openai_settings
from makeitreal.graph.state import Proposal
from makeitreal.tools import search_library_docs, search_suitable_techstack


class TechStackGeneratorAgent(RequirementsGeneratorAgent):
    """Agent responsible for generating tech stack."""

    def __init__(self) -> None:
        """Initialize the Tech Stack generator agent."""
        super().__init__()
        self.name = "TechStackGeneratorAgent"

        # Initialize tools
        self.tools = [
            search_suitable_techstack,
            search_library_docs,
        ]
        self.tool_node = ToolNode(self.tools)

        # Create a separate LLM instance for tool calling (without structured output)
        self.llm_with_tools = ChatOpenAI(
            model=openai_settings.openai_model,
            api_key=openai_settings.openai_api_key,
            base_url=openai_settings.openai_base_url,
        ).bind_tools(self.tools)

    def _kind(self) -> str:
        return "tech stack items"

    async def process(self, idea: str, proposal: Proposal) -> dict[str, Any]:
        """Generates the tech stack items into the proposal´"""
        input_data = {
            "items": "\n".join([f"{i + 1}. {x}" for i, x in enumerate(proposal.proposed_items)]),
            "idea": idea,
            "change_request": proposal.change_request,
        }

        # Check if tools should be used
        tool_response = await (self.prompt | self.llm_with_tools).ainvoke(input_data)

        # Prepare context for final structured output
        tool_context = ""

        # Check if the response contains tool calls
        if hasattr(tool_response, "tool_calls") and tool_response.tool_calls:
            print(f"TechStackAgent calling {len(tool_response.tool_calls)} tool(s)")

            # Process each tool call
            tool_results = []
            for tool_call in tool_response.tool_calls:
                print(f"TechStackAgent → {tool_call['name']}")
                tool_result = await self.tool_node.ainvoke({"messages": [tool_response]})
                tool_results.append(tool_result)

            # Create context from tool results for structured output
            tool_context = (
                "\n\nTool Research Results:\n"
                f"{chr(10).join([str(result) for result in tool_results])}"
            )

        # Update the input with tool context if available
        final_input = input_data.copy()
        if tool_context:
            final_input["idea"] = final_input["idea"].content + tool_context

        # Use structured output LLM for final result
        result = await (self.prompt | self.llm).ainvoke(final_input)

        return result.model_dump()

    def _build_system_prompt(self) -> str:
        """Build comprehensive evaluation prompt for the LLM."""
        return """
You are a senior technical requirements engineer with expertise in software development
and product management.

You have access to 2 research tools:

1. **search_suitable_techstack**: For discovering relevant technologies through web search
2. **search_library_docs**: For getting up-to-date documentation of specific libraries/frameworks

Decide intelligently when to use these tools:
- Use search_suitable_techstack if you need to discover new technologies for the project
- Use search_library_docs when you need current documentation
for specific technologies (either discovered or already known)
- You can use both tools in sequence: web search → documentation lookup
- You can also skip web search and go directly to documentation lookup if you already know
what technologies to recommend

Your task is to derive the minimum set of technology stack items needed
to implement the user's idea effectively.
Prioritize current, well-documented technologies with the latest information.
"""
