"""use-case/requirements generator agent."""

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from ..config import openai_settings
from ..graph2.state import Proposal
from .base_agent import BaseAgent


class ProposalResult(BaseModel):
    """LLM-proposed items."""

    items: list[str] = Field(..., description="Proposed items")


class RequirementsGeneratorAgent(BaseAgent):
    """Agent responsible for generating items."""

    def __init__(self) -> None:
        """Initialize the Requirements generator agent."""
        super().__init__("RequirementsGeneratorAgent")
        self.llm = ChatOpenAI(
            model=openai_settings.openai_model,
            api_key=openai_settings.openai_api_key,
            base_url=openai_settings.openai_base_url,
        ).with_structured_output(ProposalResult, method="function_calling")
        self._init_prompt()

    def _init_prompt(self):
        self.prompt = ChatPromptTemplate(
            partial_variables={
                "kind": self._kind(),
            },
            messages=[
                ("system", self._build_system_prompt()),
                (
                    "human",
                    """I have the following idea:
                 {idea}

                 Based on the idea, the following {kind} have been identified already:
                 {items}

                 I want additional changes:
                 {change_request}

                 Please list the {kind} of that idea!
                 """,
                ),
            ],
        )

    def _kind(self) -> str:
        return "use-cases"

    async def process(self, idea: str, proposal: Proposal) -> dict[str, Any]:
        """Generates the use-cases into the proposal.

        Args:
            proposal: Proposal to generate

        Returns:
            Dictionary containing structured review results
        """
        chain = self.prompt | self.llm
        result = await chain.ainvoke(
            {
                "items": "\n".join(
                    [f"{i + 1}. {x}" for i, x in enumerate(proposal.proposed_items)]
                ),
                "idea": idea,
                "change_request": proposal.change_request,
            }
        )
        print("generator results")
        print(result.model_dump())

        return result.model_dump()

    def _build_system_prompt(self) -> str:
        """Build comprehensive evaluation prompt for the LLM."""
        return """
You are a senior technical requirements engineer with expertise
in software development and product management.
Your task is to derive the minimum set of features needed from the user's idea.
"""
