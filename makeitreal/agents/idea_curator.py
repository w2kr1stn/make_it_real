"""Idea Curator agent for analyzing and structuring product ideas."""

from typing import Any

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic_settings import BaseSettings

from ..models import CurationResult
from .base import BaseAgent


class Settings(BaseSettings):
    """Configuration settings for the Idea Curator agent."""

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"

    class Config:
        env_file = ".env"


class IdeaCurator(BaseAgent):
    """Agent that curates and analyzes product ideas."""

    def __init__(self) -> None:
        """Initialize the Idea Curator agent."""
        super().__init__("Idea Curator")

        self.settings = Settings()
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_base_url,
        )

        self.parser = PydanticOutputParser(pydantic_object=CurationResult)

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
            a solid foundation for product development.

            {format_instructions}""",
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

        chain = self.prompt | self.llm | self.parser

        result = await chain.ainvoke(
            {"idea": idea, "format_instructions": self.parser.get_format_instructions()}
        )

        return {"curation_result": result.model_dump()}
