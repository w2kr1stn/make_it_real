"""Use-case review agent."""

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from makeitreal.agents.base_agent import BaseAgent
from makeitreal.config import openai_settings
from makeitreal.graph.state import WorkflowState


class ReviewResult(BaseModel):
    """The result of a review."""

    changes: str = Field(..., description="Requested changes to the proposal")
    approved: bool = Field(..., description="Set to true only when there are no changes needed")


class RequirementsReviewAgent(BaseAgent):
    """Agent responsible for evaluating technical specifications for feasibility and risk."""

    def __init__(self, proposal_key="features", kind="use-cases") -> None:
        """Initialize agent."""
        super().__init__("RequirementsReviewAgent")
        self._llm = ChatOpenAI(
            model=openai_settings.openai_model,
            api_key=openai_settings.openai_api_key,
            base_url=openai_settings.openai_base_url,
        ).with_structured_output(ReviewResult, method="function_calling")
        self._proposal_key = proposal_key
        self._prompt = self._build_prompt(kind)

    def _build_prompt(self, kind: str) -> ChatPromptTemplate:
        return ChatPromptTemplate(
            partial_variables={
                "kind": kind,
            },
            messages=[
                ("system", self._build_review_system_prompt()),
                (
                    "human",
                    """I have the following idea:
                 {idea}

                 Based on the idea, the following {kind} have been identified:
                 {items}

                 Please review the {kind} meticulously and ask yourself the following questions:
                 * Are there any {kind} missing in the list that would be required
                 to make the idea work? If so, they should be added.
                 * Are there any {kind} in the list that are not strictly required
                 for an MVP implementation? If so, they should be removed.

                 Finally please propose changes, if necessary, or approve otherwise!
                 """,
                ),
            ],
        )

    async def process(self, state: WorkflowState) -> dict[str, Any]:
        """Reviewes the suggested changes to the proposal.

        Args:
            proposal: Proposal to review

        Returns:
            Dictionary containing structured review results
        """
        proposal = state[self._proposal_key]
        chain = self._prompt | self._llm
        result = await chain.ainvoke(
            {
                "items": "\n".join(
                    [f"{i + 1}. {x}" for i, x in enumerate(proposal.proposed_items)]
                ),
                "idea": state.get("idea"),
            }
        )
        print("review results")
        print(result.model_dump())

        return result.model_dump()

    def _build_review_system_prompt(self) -> str:
        """Build comprehensive evaluation prompt for the LLM."""
        return """
You are a senior technical requirements engineer with expertise
in software development and product management.
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
