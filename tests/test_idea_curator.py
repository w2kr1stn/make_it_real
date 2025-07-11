"""Simple tests for the IdeaCurator agent focusing on structure."""

from unittest.mock import patch

import pytest

from makeitreal.agents import IdeaCurator
from makeitreal.models import CurationResult


def test_idea_curator_initialization():
    """Test that IdeaCurator initializes correctly without API calls."""
    with patch("makeitreal.agents.idea_curator.openai_settings") as mock_settings:
        mock_settings.openai_api_key = "test-key"
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_base_url = "https://api.openai.com/v1"

        with (
            patch("makeitreal.agents.idea_curator.ChatOpenAI"),
            patch("makeitreal.agents.idea_curator.PydanticOutputParser"),
            patch("makeitreal.agents.idea_curator.ChatPromptTemplate"),
        ):
            curator = IdeaCurator()
            assert curator.name == "Idea Curator"
            assert hasattr(curator, "llm")
            assert hasattr(curator, "parser")
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
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_base_url = "https://api.openai.com/v1"

        with (
            patch("makeitreal.agents.idea_curator.ChatOpenAI"),
            patch("makeitreal.agents.idea_curator.PydanticOutputParser"),
            patch("makeitreal.agents.idea_curator.ChatPromptTemplate"),
        ):
            curator = IdeaCurator()

            # Test empty input
            with pytest.raises(ValueError, match="Input data must contain 'idea' key"):
                await curator.process({})

            # Test missing idea key
            with pytest.raises(ValueError, match="Input data must contain 'idea' key"):
                await curator.process({"other_key": "value"})
