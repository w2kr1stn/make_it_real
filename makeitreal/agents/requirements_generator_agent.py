"""use-case/requirements generator agent."""

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from makeitreal.agents.base_agent import BaseAgent
from makeitreal.config import openai_settings
from makeitreal.graph.state import Proposal, WorkflowState


class ProposalResult(BaseModel):
    """LLM-proposed items."""

    items: list[str] = Field(..., description="Proposed items")


class RequirementsGeneratorAgent(BaseAgent):
    """Agent responsible for generating items."""

    def __init__(self, proposal_key="features", kind="use-cases") -> None:
        """Initialize agent."""
        super().__init__("RequirementsGeneratorAgent")
        self._llm = ChatOpenAI(
            model=openai_settings.openai_model,
            api_key=openai_settings.openai_api_key,
            base_url=openai_settings.openai_base_url,
        ).with_structured_output(ProposalResult, method="function_calling")
        self._proposal_key = proposal_key
        self._prompt = self._build_prompt(kind)

    def _build_prompt(self, kind: str) -> ChatPromptTemplate:
        return ChatPromptTemplate(
            partial_variables={
                "kind": kind,
            },
            messages=[
                ("system", self._build_system_prompt()),
                ("human", self._build_human_prompt()),
            ],
        )

    def _build_human_prompt(self) -> str:
        return """I have the following idea:
                  {idea}

                  Based on the idea, the following {kind} have been identified already:
                  {items}

                  I want additional changes:
                  {change_request}

                  Please list the {kind} of that idea!
                  """

    def _additional_variables(self, state: WorkflowState) -> dict[str, str]:
        return {}

    def _items2str(self, items: list[Proposal]) -> str:
        return "\n".join([f"{i + 1}. {x}" for i, x in enumerate(items)])

    async def process(self, state: WorkflowState) -> dict[str, Any]:
        """Generates the use-cases into the proposal.

        Args:
            proposal: Proposal to generate

        Returns:
            Dictionary containing structured review results
        """
        proposal = state[self._proposal_key]
        chain = self._prompt | self._llm
        result = await chain.ainvoke(
            {
                "items": self._items2str(proposal.proposed_items),
                "idea": state.get("idea"),
                "change_request": proposal.change_request,
            } | self._additional_variables(state)
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
