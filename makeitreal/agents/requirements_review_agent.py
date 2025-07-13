"""Evaluator agent for feasibility assessment and risk analysis."""

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config import openai_settings
from .base import BaseAgent
from ..graph2.state import Proposal
from pydantic import BaseModel, Field   


class ReviewResult(BaseModel):
    """The result of a review."""

    changes: str = Field(..., description="Requested changes to the proposal")
    approved: bool = Field(..., description="Are the suggested features approved?")


class RequirementsReviewAgent(BaseAgent):
    """Agent responsible for evaluating technical specifications for feasibility and risk."""

    def __init__(self) -> None:
        """Initialize the Requirements review agent."""
        super().__init__("RequirementsReviewAgent")
        self.llm = ChatOpenAI(
            model=openai_settings.openai_model,
            api_key=openai_settings.openai_api_key,
            base_url=openai_settings.openai_base_url,
        ).with_structured_output(
            ReviewResult, method="function_calling"
        )

    async def process(self, idea:str, proposal: Proposal) -> dict[str, Any]:
        """Reviewes the suggested changes to the proposal.

        Args:
            proposal: Proposal to review

        Returns:
            Dictionary containing structured review results
        """
        print("Process review")
        if not proposal.proposedItems:
            raise ValueError("No proposedItems provided for review")

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self._build_review_system_prompt()),
                ("human", """I have created the following list of features: 
                 {items}

                 Derived from the following idea of a person:
                 {idea}

                 Please review these features and propose changes to me if they would make sense or approve the features.
                 """),
            ]
        )

        chain = prompt | self.llm
        result = await chain.ainvoke({"items": "\n\t- ".join(proposal.proposedItems),"idea": idea})
        print("review results")
        print(result.model_dump())
        
        return result.model_dump()

    def _build_review_system_prompt(self) -> str:
        """Build comprehensive evaluation prompt for the LLM."""
        return """
You are a senior technical requirements engineer with expertise in software development and product management. 
You have the task to review a set of features which where derived by a users idea. 

Whilst reviewing the features, you will be given the opportunity to request changes to the features.

You should review the features and make sure that they are:
- complete
- consistent
- feasible
- non-contradictory
- are prioritized with a priority level which should aim for a MVP implementation
- also the list should have a reasonable size which reflects the scope of the intial idea
Be thorough, realistic, and specific in your review.
"""
