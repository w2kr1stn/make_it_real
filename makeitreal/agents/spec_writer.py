"""Spec Writer agent for generating technical specifications from curated ideas."""

from typing import Any

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config import openai_settings
from ..models import TechnicalSpec
from ..templates import PRDTemplate
from .base import BaseAgent


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

        self.template = PRDTemplate()
        self.parser = PydanticOutputParser(pydantic_object=TechnicalSpec)

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a senior technical product manager and specification expert.

Transform the curated product idea into a comprehensive technical specification
following Amazon's Working Backwards methodology.

Use this PRD template structure:
{template}

Based on the curated idea analysis:
- Product Idea: {product_idea}
- Market Analysis: {market_analysis}
- Recommended Features: {recommended_features}
- Next Steps: {next_steps}

Generate a complete PRD that includes:

1. **Press Release**: Write as if the product already launched successfully
   - Compelling headline and subtitle
   - Clear problem and solution statements
   - Engaging leader and customer quotes
   - Specific call to action

2. **FAQ**: Address both internal (technical, business) and customer questions

3. **User Stories**: Create INVEST-compliant user stories for key features
   - Format: "As a [user type], I want [capability] so that [benefit]"
   - Include acceptance criteria and definition of done

4. **Technical Requirements**: List core technical features and capabilities

5. **Success Metrics**: Define measurable KPIs and success criteria

6. **Timeline**: Provide realistic development phases and timeline

Be specific, actionable, and realistic. Focus on solving real user problems
with a clear value proposition.

{format_instructions}""",
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

        # Extract components from curation result
        product_idea = curation_result.get("product_idea", {})
        market_analysis = curation_result.get("market_analysis", {})
        recommended_features = curation_result.get("recommended_features", [])
        next_steps = curation_result.get("next_steps", [])

        chain = self.prompt | self.llm | self.parser

        result = await chain.ainvoke(
            {
                "template": self.template.get_template(),
                "product_idea": product_idea,
                "market_analysis": market_analysis,
                "recommended_features": recommended_features,
                "next_steps": next_steps,
                "format_instructions": self.parser.get_format_instructions(),
            }
        )

        return {"technical_spec": result.model_dump()}
