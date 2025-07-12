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


def test_evaluator_initialization(evaluator):
    """Test that evaluator initializes correctly."""
    assert evaluator.name == "Evaluator"
    assert evaluator.llm is not None
    assert evaluator.structured_llm is not None


@pytest.mark.asyncio
async def test_evaluator_process_success(evaluator, mock_technical_spec):
    """Test successful evaluation processing with mocked LLM."""

    # Create expected result
    mock_result = EvaluationResult(
        feasibility_score=0.85,
        resource_score=0.75,
        timeline_score=0.90,
        risk_assessment="Medium risk with manageable technical challenges.",
        recommendations=[
            "Start with core MVP features",
            "Implement comprehensive testing early",
            "Consider progressive web app approach",
            "Plan for scalability from beginning",
        ],
        go_no_go="GO",
    )

    # Mock the structured_llm chain
    async def mock_chain_invoke(inputs):
        return mock_result

    # Create a mock chain that behaves like the real one
    mock_chain = AsyncMock()
    mock_chain.ainvoke = mock_chain_invoke

    # Patch the chain creation
    with patch("makeitreal.agents.evaluator.ChatPromptTemplate") as mock_prompt:
        mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

        result = await evaluator.process({"technical_spec": mock_technical_spec})

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
async def test_evaluator_no_go_decision(evaluator, mock_technical_spec):
    """Test evaluator can make NO_GO decisions."""

    # Create NO_GO result
    mock_result = EvaluationResult(
        feasibility_score=0.25,
        resource_score=0.15,
        timeline_score=0.30,
        risk_assessment="High risk project with significant technical challenges.",
        recommendations=[
            "Reduce scope significantly",
            "Extend timeline by 6 months",
            "Consider alternative technology approaches",
        ],
        go_no_go="NO_GO",
    )

    # Mock the chain
    async def mock_chain_invoke(inputs):
        return mock_result

    mock_chain = AsyncMock()
    mock_chain.ainvoke = mock_chain_invoke

    with patch("makeitreal.agents.evaluator.ChatPromptTemplate") as mock_prompt:
        mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

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
