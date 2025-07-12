"""Tests for LangGraph workflow implementation."""

from unittest.mock import AsyncMock, patch

import pytest

from makeitreal.graph import IdeationWorkflow


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
        "recommended_features": ["Task creation", "Due dates"],
        "next_steps": ["User research", "MVP development"],
    }


@pytest.fixture
def workflow():
    """Create workflow with memory checkpointing."""
    # Mock OpenAI API key for testing
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        return IdeationWorkflow()


def test_workflow_initialization(workflow):
    """Test that workflow initializes correctly."""

    assert workflow.checkpointer is not None
    assert workflow.idea_curator is not None
    assert workflow.spec_writer is not None
    assert workflow.evaluator is not None
    assert workflow.graph is not None


@pytest.mark.asyncio
async def test_workflow_run_success(workflow, mock_curation_result):
    """Test successful workflow execution."""
    workflow = workflow

    # Mock all three agents
    with (
        patch.object(workflow.idea_curator, "process", new_callable=AsyncMock) as mock_curator,
        patch.object(workflow.spec_writer, "process", new_callable=AsyncMock) as mock_spec_writer,
        patch.object(workflow.evaluator, "process", new_callable=AsyncMock) as mock_evaluator,
    ):
        mock_curator.return_value = {"curation_result": mock_curation_result}
        mock_spec_writer.return_value = {"technical_spec": {"test": "spec"}}
        mock_evaluator.return_value = {
            "evaluation_results": {"go_no_go": "GO", "feasibility_score": 0.8}
        }

        result = await workflow.run("A task management app for professionals")

        # Verify the result structure
        assert isinstance(result, dict)
        assert "current_phase" in result
        assert "product_idea" in result
        assert "technical_spec" in result
        assert "evaluation_results" in result
        assert "error" in result
        assert result["current_phase"] == "evaluated"
        assert result["error"] == ""
        assert result["product_idea"] == mock_curation_result


@pytest.mark.asyncio
async def test_workflow_run_with_error(workflow):
    """Test workflow execution with error handling."""
    workflow = workflow

    # Mock the idea curator to raise an exception
    with patch.object(workflow.idea_curator, "process", new_callable=AsyncMock) as mock_curator:
        mock_curator.side_effect = Exception("Test error")

        result = await workflow.run("A task management app")

        # Verify error handling
        assert result["current_phase"] == "error"
        assert "Test error" in result["error"]


@pytest.mark.asyncio
async def test_workflow_state_persistence(workflow, mock_curation_result):
    """Test that workflow state is persisted in memory."""
    thread_id = "test-thread-123"

    with (
        patch.object(workflow.idea_curator, "process", new_callable=AsyncMock) as mock_curator,
        patch.object(workflow.spec_writer, "process", new_callable=AsyncMock) as mock_spec_writer,
        patch.object(workflow.evaluator, "process", new_callable=AsyncMock) as mock_evaluator,
    ):
        mock_curator.return_value = {"curation_result": mock_curation_result}
        mock_spec_writer.return_value = {"technical_spec": {"test": "spec"}}
        mock_evaluator.return_value = {
            "evaluation_results": {"go_no_go": "GO", "feasibility_score": 0.8}
        }

        # Run workflow with specific thread_id
        result = await workflow.run("Test idea", thread_id=thread_id)

        # Verify that the result contains expected data
        assert result["current_phase"] == "evaluated"
        assert result["product_idea"] == mock_curation_result


@pytest.mark.asyncio
async def test_idea_curator_node_directly(workflow, mock_curation_result):
    """Test idea curator node execution directly."""
    workflow = workflow

    # Create mock state
    mock_state = {
        "messages": [type("MockMessage", (), {"content": "Test idea"})()],
        "current_phase": "started",
        "error": "",
    }

    with patch.object(workflow.idea_curator, "process", new_callable=AsyncMock) as mock_process:
        mock_process.return_value = {"curation_result": mock_curation_result}

        result = await workflow.idea_curator_node(mock_state)

        # Verify node output
        assert result["current_phase"] == "curated"
        assert result["product_idea"] == mock_curation_result
        assert result["error"] == ""


@pytest.mark.asyncio
async def test_idea_curator_node_with_error(workflow):
    """Test idea curator node error handling."""
    workflow = workflow

    mock_state = {
        "messages": [type("MockMessage", (), {"content": "Test idea"})()],
        "current_phase": "started",
        "error": "",
    }

    with patch.object(workflow.idea_curator, "process", new_callable=AsyncMock) as mock_process:
        mock_process.side_effect = Exception("Node error")

        result = await workflow.idea_curator_node(mock_state)

        # Verify error handling
        assert result["current_phase"] == "error"
        assert "Node error" in result["error"]


def test_workflow_state_type_annotations():
    """Test that WorkflowState has correct type annotations."""
    from makeitreal.graph.state import WorkflowState

    # Verify that WorkflowState is properly defined
    annotations = WorkflowState.__annotations__

    expected_fields = [
        "messages",
        "product_idea",
        "market_analysis",
        "technical_spec",
        "evaluation_results",
        "current_phase",
        "error",
        "requires_human_review",
    ]

    for field in expected_fields:
        assert field in annotations
