"""LangGraph workflow implementation for idea processing."""

import json
import os
import uuid
from datetime import datetime
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from makeitreal.agents.base_agent import BaseAgent
from makeitreal.agents.requirements_generator_agent import RequirementsGeneratorAgent
from makeitreal.agents.requirements_review_agent import RequirementsReviewAgent
from makeitreal.agents.task_generator_agent import TaskGeneratorAgent
from makeitreal.agents.task_review_agent import TaskReviewAgent
from makeitreal.agents.techstack_generator_agent import TechStackGeneratorAgent
from makeitreal.agents.techstack_review_agent import TechStackReviewAgent
from makeitreal.graph.state import Proposal, WorkflowState


class IdeationWorkflow:
    """LangGraph workflow for processing product ideas."""

    def __init__(self):
        """Initialize the workflow with memory checkpointing."""
        self.checkpointer = MemorySaver()
        self.graph = None

    async def ainit(self):
        self.graph = await self._build_graph()

    async def _build_graph(self):
        """Build the LangGraph workflow."""
        workflow = StateGraph(WorkflowState)

        workflow.add_node(
            "requirement_analysis",
            await self._build_proposal_graph(
                "features", RequirementsGeneratorAgent(), RequirementsReviewAgent()
            ),
        )
        workflow.add_node(
            "techstack_discovery",
            await self._build_proposal_graph(
                "tech_stack", TechStackGeneratorAgent(), TechStackReviewAgent()
            ),
        )
        workflow.add_node(
            "task_creation",
            await self._build_proposal_graph("tasks", TaskGeneratorAgent(), TaskReviewAgent()),
        )
        workflow.add_node("log_tasks", self._log_tasks)

        workflow.add_edge(START, "requirement_analysis")
        workflow.add_edge("requirement_analysis", "techstack_discovery")
        workflow.add_edge("techstack_discovery", "task_creation")
        workflow.add_edge("task_creation", "log_tasks")
        workflow.add_edge("log_tasks", END)

        return workflow.compile(checkpointer=self.checkpointer)

    async def _build_proposal_graph(
        self,
        key: str,
        generator_agent: RequirementsGeneratorAgent,
        review_agent: RequirementsReviewAgent,
    ):
        """Build a LangGraph sub graph of the workflow."""
        workflow = StateGraph(WorkflowState)

        async def generate_agent_node(state):
            await self._requirement_analysis(state, key, generator_agent)

        async def review_agent_node(state):
            return await self._agent_review(state, key, review_agent)

        workflow.add_node("requirements_agent", generate_agent_node)
        workflow.add_node("review_agent", review_agent_node)
        workflow.add_node("human_review", lambda state: self._human_review(state, key))

        workflow.add_edge(START, "requirements_agent")
        workflow.add_edge("requirements_agent", "review_agent")

        workflow.add_conditional_edges(
            "review_agent",
            lambda state: state.get(key).agent_approved and "approved" or "rejected",
            {"approved": "human_review", "rejected": "requirements_agent"},
        )
        workflow.add_conditional_edges(
            "human_review",
            lambda state: state.get(key).human_approved and "approved" or "rejected",
            {"approved": END, "rejected": "requirements_agent"},
        )

        return workflow.compile()

    async def _requirement_analysis(
        self, state: WorkflowState, key: str, agent: RequirementsGeneratorAgent
    ) -> dict[str, Any]:
        print(f"{key} requirement analysis")
        proposal = state.get(key)

        result = await agent.process(proposal=proposal, idea=state.get("idea"))

        proposal.proposed_items = result["items"]
        proposal.change_request = None

        return {
            key: proposal,
        }

    async def _agent_review(
        self, state: WorkflowState, key: str, agent: BaseAgent
    ) -> dict[str, Any]:
        print(f"{key} review by agent")
        proposal = state.get(key)
        result = await agent.process(proposal=proposal, idea=state.get("idea"))
        proposal.agent_approved = result["approved"]
        proposal.change_request = result["changes"] or ""

        return {
            key: proposal,
        }

    def _human_review(self, state: WorkflowState, key: str) -> dict[str, Any]:
        print(f"{key} review by human")
        proposal = state.get(key)
        proposal.change_request = interrupt({"key": key, "state": state})
        proposal.human_approved = proposal.change_request == ""

        # proposal.human_approved = proposal.human_approved or randint(1,2) > 1
        # TODO: proposal.change_request = "Please remove feature xy"
        print(
            f"Received {key} decision: {proposal.change_request == ''}, "
            f"change_request: {proposal.change_request}"
        )

        return {
            key: proposal,
        }

    def _save_state_to_json(self, state: WorkflowState) -> None:
        """Save workflow state to JSON file."""
        os.makedirs(".state", exist_ok=True)
        filename = f".state/state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(
                {
                    "idea": state["idea"].content,
                    "features": state["features"].model_dump(),
                    "tech_stack": state["tech_stack"].model_dump(),
                    "tasks": state["tasks"].model_dump(),
                },
                f,
                indent=2,
            )
        print(f"\nState saved to {filename} ✓")

    def _log_tasks(self, state: WorkflowState) -> dict[str, Any]:
        print("TASKS:\n* " + ("\n* ".join(state.get("tasks").proposed_items)))
        self._save_state_to_json(state)
        return {}

    async def run(self, idea: str, thread_id: str = None) -> WorkflowState:
        """Execute workflow for a given idea."""
        if thread_id is None:
            thread_id = str(uuid.uuid4())

        initial_state = {
            "messages": [HumanMessage(content=idea)],
            "idea": HumanMessage(content=idea),
            "features": Proposal(),
            "tech_stack": Proposal(),
            "tasks": Proposal(),
        }
        config = {"configurable": {"thread_id": thread_id}}
        result = await self.graph.ainvoke(initial_state, config)

        self._save_state_to_json(result)

        return result
