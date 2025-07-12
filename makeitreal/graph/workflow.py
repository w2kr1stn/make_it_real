"""LangGraph workflow implementation for idea processing."""

import uuid
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from ..agents.idea_curator import IdeaCurator
from .state import WorkflowState


class IdeationWorkflow:
    """LangGraph workflow for processing product ideas."""

    def __init__(self):
        """Initialize the workflow with memory checkpointing."""
        self.checkpointer = MemorySaver()
        self.idea_curator = IdeaCurator()
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph workflow."""
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("idea_curator", self.idea_curator_node)

        # Define flow
        workflow.add_edge(START, "idea_curator")
        workflow.add_edge("idea_curator", END)

        return workflow.compile(checkpointer=self.checkpointer)

    async def idea_curator_node(self, state: WorkflowState) -> dict[str, Any]:
        """Process idea with curator agent."""
        try:
            # Extract idea from the last message
            idea = state["messages"][-1].content if state["messages"] else ""

            result = await self.idea_curator.process({"idea": idea})

            return {
                "product_idea": result["curation_result"],
                "current_phase": "curated",
                "error": "",
            }
        except Exception as e:
            return {
                "error": str(e),
                "current_phase": "error",
            }

    async def run(self, idea: str, thread_id: str = None) -> WorkflowState:
        """Execute workflow for a given idea."""
        if thread_id is None:
            thread_id = str(uuid.uuid4())

        initial_state = {
            "messages": [HumanMessage(content=idea)],
            "product_idea": {},
            "market_analysis": {},
            "technical_spec": {},
            "evaluation_results": {},
            "current_phase": "started",
            "error": "",
            "requires_human_review": False,
        }

        config = {"configurable": {"thread_id": thread_id}}
        result = await self.graph.ainvoke(initial_state, config)

        return result
