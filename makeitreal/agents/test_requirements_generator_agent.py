"""Tests for the agents module."""

import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from makeitreal.agents.requirements_generator_agent import RequirementsGeneratorAgent
from makeitreal.state.state import Proposal, WorkflowState


@pytest.mark.asyncio
async def test_requirements_generator_agent():
    state = WorkflowState(
        idea="""
        I want to have an app written in python (because i know how to write python code).
        The app should enable me to manage tasks.
        """,
        features=Proposal(),
        tech_stack=Proposal(),
        tasks=Proposal(),
    )

    answer = await RequirementsGeneratorAgent().process(state)

    test_metrics = GEval(
        name="Requirements generator agent test",
        criteria="Determine if the 'actual output' is correct based on the 'expected output'.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        threshold=0.5,
    )
    test_case = LLMTestCase(
        actual_output="\n".join(answer.get("items", [])),
        expected_output="""
        Add, edit, and delete tasks
        """,
    )


    assert_test(test_case, [test_metrics])
