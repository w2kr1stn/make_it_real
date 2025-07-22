""""Tests for the agents module."""
import pytest

from makeitreal.agents.requirements_generator_agent import RequirementsGeneratorAgent
from makeitreal.state.state import WorkflowState,Proposal
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval

@pytest.mark.asyncio
async def test_requirements_generator_agent():
    state = WorkflowState(
        idea="I want to have an app written in python (because i know how to write python code) that enables me to manges tasks",
        features=Proposal(),
        tech_stack=Proposal(),
        tasks=Proposal(),
    )

    answer = await RequirementsGeneratorAgent().process(state)

    test_metrics = GEval(
        name="Tech Stack Review Agent Test",
        criteria="Determine if the 'actual output' is correct based on the 'expected output'.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        threshold=0.5
    )
    test_case = LLMTestCase(
        input=state.get("idea"),
        actual_output="\n".join(answer.get("items",[])),
        expected_output="""
        Create and add new tasks
        View a list of all tasks
        Mark tasks as complete or incomplete
        Prioritize tasks with different levels
        """
    )
    assert_test(test_case, [test_metrics])