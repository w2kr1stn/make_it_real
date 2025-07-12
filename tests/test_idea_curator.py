"""Simple tests for the IdeaCurator agent focusing on structure."""

from unittest.mock import AsyncMock, patch

import pytest

from makeitreal.agents import IdeaCurator
from makeitreal.models import CurationResult


def test_idea_curator_initialization():
    """Test that IdeaCurator initializes correctly without API calls."""
    with patch("makeitreal.agents.idea_curator.openai_settings") as mock_settings:
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_model = "gpt-4.1-nano"
        mock_settings.openai_base_url = "https://api.openai.com/v1"

        with (
            patch("makeitreal.agents.idea_curator.ChatOpenAI"),
            patch("makeitreal.agents.idea_curator.ChatPromptTemplate"),
        ):
            curator = IdeaCurator()
            assert curator.name == "Idea Curator"
            assert hasattr(curator, "llm")
            assert hasattr(curator, "structured_llm")
            assert hasattr(curator, "prompt")


def test_curation_result_model_validation():
    """Test that CurationResult model validates correctly."""
    # Valid data should work
    valid_data = {
        "product_idea": {
            "raw_idea": "Test idea",
            "problem_statement": "Test problem",
            "target_users": ["Test user"],
            "value_proposition": "Test value",
        },
        "market_analysis": {
            "market_size": "Test market",
            "competitors": [{"name": "Test", "description": "Test desc"}],
            "opportunities": ["Test opportunity"],
            "risks": ["Test risk"],
        },
        "recommended_features": ["Feature 1"],
        "next_steps": ["Step 1"],
    }

    result = CurationResult(**valid_data)
    assert result.product_idea.raw_idea == "Test idea"
    assert len(result.market_analysis.competitors) == 1
    assert len(result.recommended_features) == 1


def test_curation_result_model_validation_error():
    """Test that CurationResult model raises validation errors for invalid data."""
    # Missing required field should fail
    invalid_data = {
        "product_idea": {
            "raw_idea": "Test idea",
            "problem_statement": "Test problem",
            "target_users": ["Test user"],
            # Missing value_proposition
        },
        "market_analysis": {
            "market_size": "Test market",
            "competitors": [],
            "opportunities": [],
            "risks": [],
        },
        "recommended_features": [],
        "next_steps": [],
    }

    with pytest.raises(ValueError):
        CurationResult(**invalid_data)


@pytest.mark.asyncio
async def test_idea_curator_input_validation():
    """Test input validation without actual LLM calls."""
    with patch("makeitreal.agents.idea_curator.openai_settings") as mock_settings:
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_model = "gpt-4.1-nano"
        mock_settings.openai_base_url = "https://api.openai.com/v1"

        with (
            patch("makeitreal.agents.idea_curator.ChatOpenAI"),
            patch("makeitreal.agents.idea_curator.ChatPromptTemplate"),
        ):
            curator = IdeaCurator()

            # Test empty input
            with pytest.raises(ValueError, match="Input data must contain 'idea' key"):
                await curator.process({})

            # Test missing idea key
            with pytest.raises(ValueError, match="Input data must contain 'idea' key"):
                await curator.process({"other_key": "value"})


@pytest.mark.asyncio
async def test_idea_curator_process_success():
    """Test successful idea curation with mocked structured output."""
    with patch("makeitreal.agents.idea_curator.openai_settings") as mock_settings:
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_model = "gpt-4.1-nano"
        mock_settings.openai_base_url = "https://api.openai.com/v1"

        # Create expected result
        mock_result = CurationResult(
            product_idea={
                "raw_idea": "task management app",
                "problem_statement": "Developers struggle with task organization",
                "target_users": ["Software developers", "Team leads"],
                "value_proposition": "Streamlined task management for dev teams",
            },
            market_analysis={
                "market_size": "Large and growing",
                "competitors": [
                    {"name": "Jira", "description": "Enterprise project management"},
                    {"name": "Trello", "description": "Visual task boards"},
                ],
                "opportunities": ["Integration with dev tools", "AI-powered prioritization"],
                "risks": ["Market saturation", "User adoption"],
            },
            recommended_features=["GitHub integration", "AI prioritization", "Team dashboards"],
            next_steps=["User interviews", "MVP prototype", "Market validation"],
        )

        # Mock the chain
        async def mock_chain_invoke(inputs):
            return mock_result

        mock_chain = AsyncMock()
        mock_chain.ainvoke = mock_chain_invoke

        with patch("makeitreal.agents.idea_curator.ChatPromptTemplate") as mock_prompt:
            mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

            curator = IdeaCurator()
            result = await curator.process({"idea": "task management app for developers"})

            # Verify result structure
            assert "curation_result" in result
            curation = result["curation_result"]
            assert curation["product_idea"]["raw_idea"] == "task management app"
            assert len(curation["market_analysis"]["competitors"]) == 2
            assert len(curation["recommended_features"]) == 3
