"""Tests for the SpecWriter agent focusing on core functionality."""

from unittest.mock import AsyncMock, patch

import pytest

from makeitreal.agents.spec_writer import SpecWriter
from makeitreal.models import FAQ, PressRelease, TechnicalSpec


@pytest.fixture
def mock_curation_result():
    """Mock curation result for testing."""
    return {
        "product_idea": {
            "raw_idea": "A task management app",
            "problem_statement": "People struggle to organize their tasks",
            "target_users": ["Professionals", "Students"],
            "value_proposition": "Simple, intuitive task organization",
        },
        "market_analysis": {
            "market_size": "Large market with growing demand",
            "competitors": [{"name": "Todoist", "description": "Feature-rich task manager"}],
            "opportunities": ["Mobile-first approach"],
            "risks": ["High competition"],
        },
        "recommended_features": ["Task creation", "Due dates", "Priority levels"],
        "next_steps": ["User research", "MVP development"],
    }


@pytest.fixture
def mock_technical_spec():
    """Mock technical specification for testing."""
    return {
        "press_release": PressRelease(
            headline="Revolutionary Task Management App Launches",
            subtitle="Simplifying productivity for professionals and students",
            intro="Our new app transforms how people organize their work and life",
            problem="People struggle with task organization and productivity",
            solution="Intuitive, mobile-first task management solution",
            leader_quote="This will change how people work",
            how_it_works="Simple three-step process for task management",
            customer_quote="Finally, a task app that just works",
            call_to_action="Download now and start organizing",
        ),
        "faq": FAQ(
            internal=["Q: How do we scale? A: Cloud infrastructure"],
            customer=["Q: Is it free? A: Freemium model"],
        ),
        "user_stories": [
            {
                "title": "As a professional, I want to create tasks",
                "description": "So that I can track my work",
                "acceptance_criteria": [
                    "Given I am a professional",
                    "When I create a task",
                    "Then I should see it in my list",
                ],
                "definition_of_done": ["Code reviewed", "Tests passing"],
                "priority": "high",
                "estimate": "3 points",
            }
        ],
        "technical_requirements": [
            "User authentication",
            "Task CRUD operations",
            "Mobile responsive design",
        ],
        "success_metrics": ["Daily active users", "Task completion rate", "User retention"],
        "timeline": "3 months to MVP, 6 months to full launch",
    }


def test_spec_writer_initialization():
    """Test that SpecWriter initializes correctly without API calls."""
    with patch("makeitreal.agents.spec_writer.openai_settings") as mock_settings:
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_model = "gpt-4.1-nano"
        mock_settings.openai_base_url = "https://api.openai.com/v1"

        with (
            patch("makeitreal.agents.spec_writer.ChatOpenAI"),
            patch("makeitreal.agents.spec_writer.ChatPromptTemplate"),
        ):
            spec_writer = SpecWriter()
            assert spec_writer.name == "Spec Writer"
            assert hasattr(spec_writer, "llm")
            assert hasattr(spec_writer, "structured_llm")


@pytest.mark.asyncio
async def test_spec_writer_input_validation():
    """Test input validation without actual LLM calls."""
    with patch("makeitreal.agents.spec_writer.openai_settings") as mock_settings:
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_model = "gpt-4.1-nano"
        mock_settings.openai_base_url = "https://api.openai.com/v1"

        with (
            patch("makeitreal.agents.spec_writer.ChatOpenAI"),
            patch("makeitreal.agents.spec_writer.ChatPromptTemplate"),
        ):
            spec_writer = SpecWriter()

            # Test empty input
            with pytest.raises(ValueError, match="Input data must contain 'curation_result'"):
                await spec_writer.process({})

            # Test missing curation_result key
            with pytest.raises(ValueError, match="Input data must contain 'curation_result'"):
                await spec_writer.process({"other_key": "value"})


def test_technical_spec_model_validation(mock_technical_spec):
    """Test that TechnicalSpec model validates correctly."""
    spec = TechnicalSpec(**mock_technical_spec)

    assert spec.press_release.headline == "Revolutionary Task Management App Launches"
    assert len(spec.user_stories) == 1
    assert len(spec.technical_requirements) == 3
    assert spec.timeline == "3 months to MVP, 6 months to full launch"


def test_technical_spec_model_validation_error():
    """Test that TechnicalSpec model raises validation errors for invalid data."""
    # Test completely empty data
    with pytest.raises(ValueError):
        TechnicalSpec()

    # Test missing required fields
    with pytest.raises(ValueError):
        TechnicalSpec(press_release={}, faq={})


@pytest.mark.asyncio
async def test_spec_writer_process_success(mock_curation_result):
    """Test successful spec writing with mocked structured output."""
    with patch("makeitreal.agents.spec_writer.openai_settings") as mock_settings:
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_model = "gpt-4.1-nano"
        mock_settings.openai_base_url = "https://api.openai.com/v1"

        # Create expected result
        mock_result = TechnicalSpec(
            press_release=PressRelease(
                headline="Revolutionary Task Management App Launches",
                subtitle="Simplifying productivity for everyone",
                intro="A new era of task management begins",
                problem="Task organization is complex",
                solution="Our app makes it simple",
                leader_quote="This changes everything",
                how_it_works="Three simple steps",
                customer_quote="Best app ever",
                call_to_action="Download today",
            ),
            faq=FAQ(
                internal=["Q: Tech stack? A: Modern cloud"],
                customer=["Q: Price? A: Free to start"],
            ),
            user_stories=[
                {
                    "title": "As a user, I want to create tasks",
                    "description": "So I can track my work",
                    "acceptance_criteria": ["Task creation works"],
                    "definition_of_done": ["Tests pass"],
                    "priority": "high",
                    "estimate": "3 points",
                }
            ],
            technical_requirements=["Auth system", "Database", "API"],
            success_metrics=["User growth", "Retention"],
            timeline="3 months MVP",
        )

        # Mock the chain
        async def mock_chain_invoke(inputs):
            return mock_result

        mock_chain = AsyncMock()
        mock_chain.ainvoke = mock_chain_invoke

        with (
            patch("makeitreal.agents.spec_writer.ChatPromptTemplate") as mock_prompt,
        ):
            mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

            spec_writer = SpecWriter()
            result = await spec_writer.process({"curation_result": mock_curation_result})

            # Verify result structure
            assert "technical_spec" in result
            spec = result["technical_spec"]
            assert spec["press_release"]["headline"] == "Revolutionary Task Management App Launches"
            assert len(spec["user_stories"]) == 1
            assert len(spec["technical_requirements"]) == 3
