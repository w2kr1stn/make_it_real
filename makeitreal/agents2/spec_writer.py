# ruff: noqa: E501
"""Spec Writer agent for generating technical specifications from curated ideas."""

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config import openai_settings
from ..models import TechnicalSpec
from .base_review_agent import BaseAgent


class SpecWriter(BaseAgent):
    """Agent that generates technical specifications from curated product ideas."""

    def __init__(self) -> None:
        """Initialize the Spec Writer agent."""
        super().__init__("Spec Writer")

        self.llm = ChatOpenAI(
            model=openai_settings.openai_model,
            api_key=openai_settings.openai_api_key,
            base_url=openai_settings.openai_base_url,
        )
        self.structured_llm = self.llm.with_structured_output(
            TechnicalSpec, method="function_calling"
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a senior technical product manager.

Transform the curated product idea into a technical specification.

Curated idea:
{curation_summary}

You MUST generate a TechnicalSpec object with these EXACT fields in this order:
- press_release (dict): Contains headline, subtitle, intro, problem, solution, leader_quote, how_it_works, customer_quote, call_to_action
- faq (dict): Contains internal (list of strings) and customer (list of strings)
- user_stories (list): Each story has title, description, acceptance_criteria, definition_of_done, priority, estimate
- technical_requirements (list of strings)
- success_metrics (list of strings)
- timeline (string)

ALL fields are required. Generate complete content for each field.""",
                ),
                (
                    "human",
                    "Generate technical specification for the curated product idea.",
                ),
            ]
        )

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process curated idea and return technical specification.

        Args:
            input_data: Dictionary containing curation_result from IdeaCurator

        Returns:
            Dictionary containing 'technical_spec' with complete PRD
        """
        curation_result = input_data.get("curation_result", {})
        if not curation_result:
            raise ValueError("Input data must contain 'curation_result' from IdeaCurator")

        chain = self.prompt | self.structured_llm

        result = await chain.ainvoke({"curation_summary": str(curation_result)})

        return {"technical_spec": result.model_dump()}
