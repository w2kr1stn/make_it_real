"""Tests for Evaluator agent."""

from unittest.mock import AsyncMock, patch

import pytest

from makeitreal.agents.evaluator import Evaluator
from makeitreal.models import EvaluationResult


@pytest.fixture
def evaluator():
    """Create evaluator instance for testing."""
    # Mock OpenAI API key for testing
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        return Evaluator()


@pytest.fixture
def mock_technical_spec():
    """Mock technical specification for testing."""
    return {
        "press_release": {
            "headline": "Revolutionary Task Management App",
            "intro": "A new approach to productivity",
        },
        "user_stories": [
            {
                "title": "As a user, I want to create tasks",
                "description": "So I can organize my work",
                "acceptance_criteria": ["Task creation form", "Task validation"],
                "priority": "high",
            }
        ],
        "technical_requirements": ["React frontend", "FastAPI backend", "PostgreSQL database"],
        "timeline": "3 months development",
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response with valid JSON."""
    return """
Based on the technical specification, here's my evaluation:

{
    "feasibility_score": 0.85,
    "resource_score": 0.75,
    "timeline_score": 0.90,
    "risk_assessment": (
        "Medium risk with manageable technical challenges. The chosen technology stack is "
        "well-established and the scope is reasonable for a 3-month timeline."
    ),
    "recommendations": [
        "Start with core MVP features to validate user needs",
        "Implement comprehensive testing early in development",
        "Consider progressive web app approach for faster deployment",
        "Plan for scalability from the beginning"
    ],
    "go_no_go": "GO"
}
"""


def test_evaluator_initialization(evaluator):
    """Test that evaluator initializes correctly."""
    assert evaluator.name == "Evaluator"
    assert evaluator.llm is not None


@pytest.mark.asyncio
async def test_evaluator_process_success(evaluator, mock_technical_spec, mock_llm_response):
    """Test successful evaluation processing."""

    # Mock the LLM response
    mock_response = type("MockResponse", (), {"content": mock_llm_response})()

    with patch.object(evaluator, "llm") as mock_llm:
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await evaluator.process({"technical_spec": mock_technical_spec})

        # Verify LLM was called with evaluation prompt
        mock_llm.ainvoke.assert_called_once()
        call_args = mock_llm.ainvoke.call_args[0][0]
        assert "TECHNICAL SPECIFICATION:" in call_args
        assert "press_release" in str(mock_technical_spec).lower()

        # Verify result structure
        assert "evaluation_results" in result
        evaluation = result["evaluation_results"]

        # Verify evaluation scores
        assert evaluation["feasibility_score"] == 0.85
        assert evaluation["resource_score"] == 0.75
        assert evaluation["timeline_score"] == 0.90
        assert evaluation["go_no_go"] == "GO"
        assert len(evaluation["recommendations"]) == 4


@pytest.mark.asyncio
async def test_evaluator_process_no_spec_error(evaluator):
    """Test evaluation fails when no technical spec provided."""

    with pytest.raises(ValueError, match="No technical specification provided"):
        await evaluator.process({})

    with pytest.raises(ValueError, match="No technical specification provided"):
        await evaluator.process({"technical_spec": {}})


@pytest.mark.asyncio
async def test_evaluator_process_json_parsing_fallback(evaluator, mock_technical_spec):
    """Test fallback behavior when LLM response is not valid JSON."""

    # Mock LLM response without valid JSON
    mock_response = type(
        "MockResponse", (), {"content": "This is a non-JSON response about the evaluation..."}
    )()

    with patch.object(evaluator, "llm") as mock_llm:
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await evaluator.process({"technical_spec": mock_technical_spec})

        # Verify fallback evaluation was created
        evaluation = result["evaluation_results"]
        assert evaluation["feasibility_score"] == 0.7
        assert evaluation["resource_score"] == 0.6
        assert evaluation["timeline_score"] == 0.7
        assert evaluation["go_no_go"] == "GO"
        assert "parsing failed" in evaluation["risk_assessment"].lower()


@pytest.mark.asyncio
async def test_evaluator_no_go_decision(evaluator, mock_technical_spec):
    """Test evaluator can make NO_GO decisions."""

    no_go_response = """
{
    "feasibility_score": 0.25,
    "resource_score": 0.15,
    "timeline_score": 0.30,
    "risk_assessment": (
        "High risk project with significant technical challenges and unrealistic timeline "
        "expectations."
    ),
    "recommendations": [
        "Reduce scope significantly",
        "Extend timeline by 6 months",
        "Consider alternative technology approaches"
    ],
    "go_no_go": "NO_GO"
}
"""

    mock_response = type("MockResponse", (), {"content": no_go_response})()

    with patch.object(evaluator, "llm") as mock_llm:
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await evaluator.process({"technical_spec": mock_technical_spec})

        evaluation = result["evaluation_results"]
        assert evaluation["go_no_go"] == "NO_GO"
        assert evaluation["feasibility_score"] == 0.25
        assert evaluation["resource_score"] == 0.15
        assert evaluation["timeline_score"] == 0.30


def test_evaluation_result_validation():
    """Test EvaluationResult model validation."""

    # Valid evaluation result
    valid_evaluation = EvaluationResult(
        feasibility_score=0.8,
        resource_score=0.7,
        timeline_score=0.9,
        risk_assessment="Low risk assessment",
        recommendations=["Recommendation 1", "Recommendation 2"],
        go_no_go="GO",
    )
    assert valid_evaluation.feasibility_score == 0.8
    assert valid_evaluation.go_no_go == "GO"

    # Invalid score (outside 0-1 range)
    with pytest.raises(ValueError):
        EvaluationResult(
            feasibility_score=1.5,  # Invalid: > 1.0
            resource_score=0.7,
            timeline_score=0.9,
            risk_assessment="Test",
            recommendations=["Test"],
            go_no_go="GO",
        )

    # Invalid go_no_go value
    with pytest.raises(ValueError):
        EvaluationResult(
            feasibility_score=0.8,
            resource_score=0.7,
            timeline_score=0.9,
            risk_assessment="Test",
            recommendations=["Test"],
            go_no_go="MAYBE",  # Invalid: only GO or NO_GO allowed
        )


@pytest.mark.asyncio
async def test_evaluator_prompt_construction(evaluator, mock_technical_spec):
    """Test that evaluation prompt is properly constructed."""

    mock_response = type("MockResponse", (), {"content": "{}"})()

    with patch.object(evaluator, "llm") as mock_llm:
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        await evaluator.process({"technical_spec": mock_technical_spec})

        # Get the prompt that was sent to LLM
        prompt = mock_llm.ainvoke.call_args[0][0]

        # Verify key sections are included
        assert "TECHNICAL FEASIBILITY" in prompt
        assert "RESOURCE REQUIREMENTS" in prompt
        assert "TIMELINE ASSESSMENT" in prompt
        assert "RISK ANALYSIS" in prompt
        assert "RECOMMENDATIONS" in prompt
        assert "GO/NO-GO DECISION" in prompt
        assert "RESPONSE FORMAT (JSON)" in prompt

        # Verify technical spec is included
        assert str(mock_technical_spec) in prompt or "press_release" in prompt
