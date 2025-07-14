"""tech stack generator agent."""

from typing import Any

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from ..config import openai_settings
from ..graph2.state import Proposal
from ..tools import search_suitable_techstack
from .requirements_generator_agent import RequirementsGeneratorAgent


class TechStackGeneratorAgent(RequirementsGeneratorAgent):
    """Agent responsible for generating tech stack."""

    def __init__(self) -> None:
        """Initialize the Tech Stack generator agent."""
        super().__init__()
        self.name = "TechStackGeneratorAgent"

        # Initialize tools
        self.tools = [search_suitable_techstack]
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
        """Generates the tech stack items into the proposal.

        Args:
            idea: The original idea
            proposal: Proposal to generate

        Returns:
            Dictionary containing structured review results
        """
        input_data = {
            "items": "\n".join([f"{i + 1}. {x}" for i, x in enumerate(proposal.proposedItems)]),
            "idea": idea,
            "changeRequest": proposal.changeRequest,
        }

        print("\nTechStackGeneratorAgent Tool-Calling Debug:")

        # Check if tools should be used
        tool_chain = self.prompt | self.llm_with_tools
        tool_response = await tool_chain.ainvoke(input_data)

        print(f"Initial LLM response type: {type(tool_response)}")

        # Prepare context for final structured output
        tool_context = ""

        # Check if the response contains tool calls
        if hasattr(tool_response, "tool_calls") and tool_response.tool_calls:
            print(f"Tool calls detected: {len(tool_response.tool_calls)} calls")

            # Process each tool call
            tool_results = []
            for i, tool_call in enumerate(tool_response.tool_calls):
                print(f"\nTool Call {i + 1}:")
                print(f"  - Tool: {tool_call['name']}")
                print(f"  - Args: {tool_call['args']}")

                # Execute the tool call through tool_node
                tool_result = await self.tool_node.ainvoke({"messages": [tool_response]})

                print(f"  - Result: {tool_result}")
                tool_results.append(tool_result)

            # Create context from tool results for structured output
            tool_context = (
                "\n\nTool Research Results:"
                f"\n{chr(10).join([str(result) for result in tool_results])}"
            )
            print(f"\nTool context prepared: {tool_context[:200]}...")

        else:
            print("No tool calls detected, proceeding with direct structured output")

        # Always generate structured output (with or without tool context)
        print("\nGenerating structured output...")

        # Update the input with tool context if available
        if tool_context:
            enhanced_input = input_data.copy()
            enhanced_input["idea"] = enhanced_input["idea"] + tool_context
            final_input = enhanced_input
        else:
            final_input = input_data

        # Use structured output LLM for final result
        structured_chain = self.prompt | self.llm
        result = await structured_chain.ainvoke(final_input)

        print("\nFinal generator results:")
        print(result.model_dump())
        print("=== End Tool-Calling Debug ===\n")

        return result.model_dump()

    def _build_system_prompt(self) -> str:
        """Build comprehensive evaluation prompt for the LLM."""
        return """
You are a senior technical requirements engineer with expertise in software development and product
management.

You have access to tools that can help you research and identify suitable technologies
for implementing the user's idea.
When suggesting tech stack items, you should:
1. Consider using the search_suitable_techstack tool to find relevant technologies
2. Base your recommendations on the search results when available
3. Provide specific, actionable tech stack items that align with the project requirements

Your task is to derive the minimum set of technology stack items needed
to implement the user's idea effectively.
"""
