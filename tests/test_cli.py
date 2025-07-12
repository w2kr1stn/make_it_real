"""Tests for the CLI module."""

from unittest.mock import patch

from typer.testing import CliRunner

from makeitreal.cli import app


def test_cli_app_exists():
    """Test that the CLI app is properly initialized."""
    assert app is not None
    assert hasattr(app, "command")


@patch("makeitreal.cli.simple_llm_call")
def test_idea_command_success(mock_llm_call):
    """Test successful idea command execution."""
    mock_llm_call.return_value = "## Test Analysis\nThis is a test response"

    runner = CliRunner()
    result = runner.invoke(app, ["test task management app"])

    assert result.exit_code == 0
    assert "Product Analysis" in result.stdout
    mock_llm_call.assert_called_once_with("test task management app")


@patch("makeitreal.cli.simple_llm_call")
def test_idea_command_with_verbose(mock_llm_call):
    """Test idea command with verbose flag."""
    mock_llm_call.return_value = "## Test Analysis\nThis is a test response"

    runner = CliRunner()
    result = runner.invoke(app, ["test app", "--verbose"])

    assert result.exit_code == 0
    assert "Processing idea:" in result.stdout
    mock_llm_call.assert_called_once_with("test app")


@patch("makeitreal.cli.simple_llm_call")
def test_idea_command_error_handling(mock_llm_call):
    """Test error handling in idea command."""
    mock_llm_call.side_effect = Exception("API Error")

    runner = CliRunner()
    result = runner.invoke(app, ["test app"])

    assert result.exit_code == 1
    assert "Error:" in result.stdout
