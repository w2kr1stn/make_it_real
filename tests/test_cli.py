"""Tests for the CLI module with IdeaCurator agent."""

from unittest.mock import AsyncMock, patch

from typer.testing import CliRunner

from makeitreal.cli import app


def test_cli_app_exists():
    """Test that the CLI app is properly initialized."""
    assert app is not None
    assert hasattr(app, "command")


@patch("makeitreal.cli.IdeaCurator")
def test_idea_command_success(mock_curator_class):
    """Test successful idea command execution with IdeaCurator."""
    # Create mock instance and result
    mock_curator = AsyncMock()
    mock_curator_class.return_value = mock_curator

    mock_result = {
        "curation_result": {
            "product_idea": {
                "raw_idea": "test task management app",
                "problem_statement": "Teams need better task coordination",
                "target_users": ["Remote workers", "Project managers"],
                "value_proposition": "Streamlined task management",
            },
            "market_analysis": {
                "market_size": "$2B market",
                "competitors": [{"name": "Asana", "description": "Project management"}],
                "opportunities": ["AI integration"],
                "risks": ["Market saturation"],
            },
            "recommended_features": ["Real-time sync", "Mobile app"],
            "next_steps": ["User interviews", "MVP wireframes"],
        }
    }
    mock_curator.process.return_value = mock_result

    runner = CliRunner()
    result = runner.invoke(app, ["test task management app"])

    assert result.exit_code == 0
    assert "Product Concept" in result.stdout
    mock_curator.process.assert_called_once_with({"idea": "test task management app"})


@patch("makeitreal.cli.IdeaCurator")
def test_idea_command_with_verbose(mock_curator_class):
    """Test idea command with verbose flag."""
    mock_curator = AsyncMock()
    mock_curator_class.return_value = mock_curator

    mock_result = {
        "curation_result": {
            "product_idea": {
                "raw_idea": "test app",
                "problem_statement": "Test problem",
                "target_users": ["Test users"],
                "value_proposition": "Test value",
            },
            "market_analysis": {
                "market_size": "Test market",
                "competitors": [],
                "opportunities": ["Test opportunity"],
                "risks": ["Test risk"],
            },
            "recommended_features": ["Test feature"],
            "next_steps": ["Test step"],
        }
    }
    mock_curator.process.return_value = mock_result

    runner = CliRunner()
    result = runner.invoke(app, ["test app", "--verbose"])

    assert result.exit_code == 0
    assert "Processing idea:" in result.stdout


@patch("makeitreal.cli.IdeaCurator")
def test_idea_command_error_handling(mock_curator_class):
    """Test error handling in idea command."""
    mock_curator = AsyncMock()
    mock_curator_class.return_value = mock_curator
    mock_curator.process.side_effect = Exception("API Error")

    runner = CliRunner()
    result = runner.invoke(app, ["test app"])

    assert result.exit_code == 1
    assert "Error:" in result.stdout
