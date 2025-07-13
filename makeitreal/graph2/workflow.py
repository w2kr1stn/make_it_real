"""LangGraph workflow implementation for idea processing."""

import uuid
from random import randint
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from .state import WorkflowState, Proposal


class IdeationWorkflow:
    """LangGraph workflow for processing product ideas."""

    def __init__(self):
        """Initialize the workflow with memory checkpointing."""
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph workflow."""
        workflow = StateGraph(WorkflowState)

        workflow.add_node("requirement_analysis", self._build_proposal_graph("features")) #params: reviewAgent:xy, requirementAgenzt:foo
        workflow.add_node("techstack_discovery", self._build_proposal_graph("techStack"))   #params: reviewAgent:bla, requirementAgenzt:blub
        #marketAnalyse propaselGraph #params: reviewAgent:marktReview, requirementAgent:markRequirements
        workflow.add_node("task_creation", self._build_proposal_graph("tasks"))
        workflow.add_node("log_tasks", self._log_tasks)

        workflow.add_edge(START, "requirement_analysis")
        workflow.add_edge("requirement_analysis", "techstack_discovery")
        workflow.add_edge("techstack_discovery", "task_creation")
        workflow.add_edge("task_creation", "log_tasks")
        workflow.add_edge("log_tasks", END)

        return workflow.compile(checkpointer=self.checkpointer)

    def _build_proposal_graph(self, key: str):
        """Build a LangGraph sub graph of the workflow."""
        workflow = StateGraph(WorkflowState)

        workflow.add_node("requirements_agent", lambda state: self._requirement_analysis(state, key))
        workflow.add_node("review_agent", lambda state: self._agent_review(state, key))
        workflow.add_node("human_review", lambda state: self._human_review(state, key))

        workflow.add_edge(START, "requirements_agent")
        workflow.add_edge("requirements_agent", "review_agent")
        # workflow.add_conditional_edges(
        #     START,
        #     lambda state: state.get(key).humanApproved and "done" or "work",
        #     {"done": END ,
        #      "work": "requirements_agent"},
        # )
        workflow.add_conditional_edges(
            "review_agent",
            lambda state: state.get(key).agentApproved and "approved" or "rejected",
            {"approved": "human_review" ,
             "rejected": "requirements_agent"},
        )
        workflow.add_conditional_edges(
            "human_review",
            lambda state: state.get(key).humanApproved and "approved" or "rejected",
            {"approved": END,
             "rejected": "requirements_agent"},
        )

        return workflow.compile()

    def _requirement_analysis(self, state: WorkflowState, key: str) -> dict[str, Any]:
        print(f"{key} requirement analysis")
        proposal = state.get(key)
        proposal.proposedItems = proposal.proposedItems or [
            f"{key} item 1",
            f"{key} item 2",
            f"{key} item 3",
            f"{key} item 4",
            f"{key} item 5",
        ]

        proposal.changeRequest = None

        return {
            key: proposal,
            "phase": key,
        }

    def _agent_review(self, state: WorkflowState, key: str) -> dict[str, Any]:
        print(f"{key} review by agent")
        proposal = state.get(key)
        proposal.agentApproved = proposal.agentApproved or randint(1,2) > 1
        proposal.changeRequest = "Add the missing feature xy"

        return {
            key: proposal,
            "phase": key,
        }

    def _human_review(self, state: WorkflowState, key: str) -> dict[str, Any]:
        print(f"{key} review by human")
        proposal = state.get(key)

        decision = interrupt(
            {
                key: proposal,
                "phase": key,
            }
        )

        proposal.humanApproved = decision

        # proposal.humanApproved = proposal.humanApproved or randint(1,2) > 1
        # TODO:: proposal.changeRequest = "Please remove feature xy"
        print(f"Received {key} decision: {decision}")

        return {
            key: proposal,
            "phase": key,
        }

    def _log_tasks(self, state: WorkflowState) -> dict[str, Any]:
        print("TASKS:\n* "+('\n* '.join(state.get('tasks').proposedItems)))
        return {}

    async def run(self, idea: str, thread_id: str = None) -> WorkflowState:
        """Execute workflow for a given idea."""
        if thread_id is None:
            thread_id = str(uuid.uuid4())

        initial_state = {
            #TODO: check if props can be accessed directly
            "messages": [HumanMessage(content=idea)],
            "idea": HumanMessage(content=idea),
            "features": Proposal(),
            "techStack": Proposal(),
            "tasks": Proposal(),
            "phase": "features",
        }
        config = {"configurable": {"thread_id": thread_id}}
        result = await self.graph.ainvoke(initial_state, config)

        return result
