"""Evaluator agent for feasibility assessment and risk analysis."""

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config import openai_settings
from .base_agent import BaseAgent
from ..graph2.state import Proposal
from pydantic import BaseModel, Field


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
        ).with_structured_output(
            ProposalResult, method="function_calling"
        )

    async def process(self, idea:str, proposal: Proposal) -> dict[str, Any]:
        """Generates the use-cases into the proposal.

        Args:
            proposal: Proposal to generate

        Returns:
            Dictionary containing structured review results
        """
        print("Generate items")
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self._build_system_prompt()),
                ("human", """There is an existing list of use-cases defined:
                 {items}

                 The features are derived from the user's idea:
                 {idea}

                 Additional changes the user wants:
                 {changeRequest}

                 Please list the use-cases of that idea!
                 """),
            ]
        )

        chain = prompt | self.llm
        result = await chain.ainvoke({
            "items": "\n\t- ".join(proposal.proposedItems),
            "idea": idea,
            "changeRequest": proposal.changeRequest,
        })
        print("generator results")
        print(result.model_dump())

        return result.model_dump()

    def _build_system_prompt(self) -> str:
        """Build comprehensive evaluation prompt for the LLM."""
        return """
You are a senior technical requirements engineer with expertise in software development and product management.
Your task is to derive the minimum set of features needed from the user's idea.
"""
