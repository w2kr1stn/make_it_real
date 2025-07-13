"""Evaluator agent for feasibility assessment and risk analysis."""

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config import openai_settings
from ..models import EvaluationResult
from .base_review_agent import BaseAgent


class Evaluator(BaseAgent):
    """Agent responsible for evaluating technical specifications for feasibility and risk."""

    def __init__(self) -> None:
        """Initialize the Evaluator agent."""
        super().__init__("Evaluator")
        self.llm = ChatOpenAI(
            model=openai_settings.openai_model,
            api_key=openai_settings.openai_api_key,
            base_url=openai_settings.openai_base_url,
        )
        self.structured_llm = self.llm.with_structured_output(
            EvaluationResult, method="function_calling"
        )

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Evaluate technical specification for feasibility and implementation risk.

        Args:
            input_data: Dictionary containing 'technical_spec' from SpecWriter

        Returns:
            Dictionary containing structured evaluation results
        """
        technical_spec = input_data.get("technical_spec", {})

        if not technical_spec:
            raise ValueError("No technical specification provided for evaluation")

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self._build_evaluation_prompt()),
                ("human", "Technical Specification to evaluate: {spec}"),
            ]
        )

        chain = prompt | self.structured_llm
        result = await chain.ainvoke({"spec": str(technical_spec)})

        return {"evaluation_results": result.model_dump()}

    def _build_evaluation_prompt(self) -> str:
        """Build comprehensive evaluation prompt for the LLM."""
        return """
You are a senior technical evaluator with expertise in software development and product management.

Evaluate the provided technical specification for a new product.

Provide a comprehensive evaluation addressing:

1. TECHNICAL FEASIBILITY (Score 0.0-1.0)
   - Architecture complexity and implementation challenges
   - Technology stack appropriateness
   - Integration complexity with existing systems
   - Scalability considerations

2. RESOURCE REQUIREMENTS (Score 0.0-1.0)
   - Team size and skill requirements
   - Development timeline realism
   - Infrastructure and tooling needs
   - Budget considerations

3. TIMELINE ASSESSMENT (Score 0.0-1.0)
   - Estimated development time accuracy
   - Dependencies and blocking factors
   - Risk buffer adequacy
   - Milestone achievability

4. RISK ANALYSIS
   - Technical risks and mitigation strategies
   - Market and competitive risks
   - Resource and timeline risks
   - Overall risk level assessment

5. RECOMMENDATIONS
   - Specific actionable recommendations
   - Priority adjustments if needed
   - Risk mitigation strategies
   - Success factors

6. GO/NO-GO DECISION
   - Clear recommendation: GO or NO_GO
   - Key decision factors
   - Conditions for success

Be thorough, realistic, and specific in your evaluation.
"""
