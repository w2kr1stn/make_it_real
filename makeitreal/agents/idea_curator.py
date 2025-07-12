"""Idea Curator agent for analyzing and structuring product ideas."""

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config import openai_settings
from ..models import CurationResult
from .base import BaseAgent


class IdeaCurator(BaseAgent):
    """Agent that curates and analyzes product ideas."""

    def __init__(self) -> None:
        """Initialize the Idea Curator agent."""
        super().__init__("Idea Curator")

        self.llm = ChatOpenAI(
            model=openai_settings.openai_model,
            api_key=openai_settings.openai_api_key,
            base_url=openai_settings.openai_base_url,
        )
        self.structured_llm = self.llm.with_structured_output(
            CurationResult, method="function_calling"
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert product strategist and market analyst.

            Analyze the given product idea and provide comprehensive structured feedback:

            1. **Problem Analysis**: Identify the core problem being solved
            2. **Target Users**: Define specific user segments who would benefit
            3. **Value Proposition**: Articulate the unique value delivered
            4. **Market Research**: Assess market size, competitors, opportunities and risks
            5. **Feature Prioritization**: Recommend key features for initial implementation
            6. **Next Steps**: Provide actionable validation steps

            Be specific, actionable, and realistic in your analysis. Focus on creating
            a solid foundation for product development.""",
                ),
                ("human", "Product Idea: {idea}"),
            ]
        )

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process a product idea and return structured curation results.

        Args:
            input_data: Dictionary containing 'idea' key with the product idea

        Returns:
            Dictionary containing 'curation_result' with structured analysis
        """
        idea = input_data.get("idea", "")
        if not idea:
            raise ValueError("Input data must contain 'idea' key with product idea")

        chain = self.prompt | self.structured_llm
        result = await chain.ainvoke({"idea": idea})

        return {"curation_result": result.model_dump()}
