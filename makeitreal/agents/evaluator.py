"""Evaluator agent for feasibility assessment and risk analysis."""

import json
import re
from typing import Any

from langchain_openai import ChatOpenAI

from ..models import EvaluationResult
from .base import BaseAgent


class Evaluator(BaseAgent):
    """Agent responsible for evaluating technical specifications for feasibility and risk."""

    def __init__(self) -> None:
        """Initialize the Evaluator agent."""
        super().__init__("Evaluator")
        self.llm = ChatOpenAI(model="gpt-4")

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

        evaluation_prompt = self._build_evaluation_prompt(technical_spec)
        response = await self.llm.ainvoke(evaluation_prompt)

        evaluation_result = self._parse_evaluation_response(response.content)

        return {"evaluation_results": evaluation_result.model_dump()}

    def _build_evaluation_prompt(self, technical_spec: dict[str, Any]) -> str:
        """Build comprehensive evaluation prompt for the LLM."""
        return f"""
You are a senior technical evaluator with expertise in software development and product management.

Evaluate this technical specification for a new product:

TECHNICAL SPECIFICATION:
{json.dumps(technical_spec, indent=2)}

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

RESPONSE FORMAT (JSON):
{{
    "feasibility_score": 0.85,
    "resource_score": 0.75,
    "timeline_score": 0.90,
    "risk_assessment": "Medium risk with manageable technical challenges...",
    "recommendations": ["Start with core MVP features", "Implement robust testing early", "..."],
    "go_no_go": "GO"
}}

Provide only the JSON response with realistic scores and detailed analysis.
"""

    def _parse_evaluation_response(self, response_content: str) -> EvaluationResult:
        """Parse LLM response into structured EvaluationResult."""
        try:
            # Extract JSON from response
            json_match = re.search(r"\{.*\}", response_content, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in evaluation response")

            json_str = json_match.group()
            evaluation_data = json.loads(json_str)

            # Validate and create EvaluationResult
            evaluation_result = EvaluationResult(**evaluation_data)
            return evaluation_result

        except (json.JSONDecodeError, ValueError) as e:
            # Fallback parsing for non-JSON responses
            return self._fallback_parse_evaluation(response_content, str(e))

    def _fallback_parse_evaluation(self, response_content: str, error_msg: str) -> EvaluationResult:
        """Fallback parsing when JSON extraction fails."""
        # Simple fallback with conservative scores
        return EvaluationResult(
            feasibility_score=0.7,
            resource_score=0.6,
            timeline_score=0.7,
            risk_assessment=(
                f"Evaluation parsing failed: {error_msg}. Conservative assessment applied."
            ),
            recommendations=[
                "Review technical specification completeness",
                "Conduct detailed technical analysis",
                "Validate resource requirements",
            ],
            go_no_go="GO",
        )
