"""LangGraph workflow implementation for idea processing."""

import uuid
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from ..agents.evaluator import Evaluator
from ..agents.idea_curator import IdeaCurator
from ..agents.spec_writer import SpecWriter
from .human_review import human_review_node
from .state import WorkflowState


class IdeationWorkflow:
    """LangGraph workflow for processing product ideas."""

    def __init__(self):
        """Initialize the workflow with memory checkpointing."""
        self.checkpointer = MemorySaver()
        self.idea_curator = IdeaCurator()
        self.spec_writer = SpecWriter()
        self.evaluator = Evaluator()
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph workflow."""
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("idea_curator", self.idea_curator_node)
        workflow.add_node("spec_writer", self.spec_writer_node)
        workflow.add_node("evaluator", self.evaluator_node)
        workflow.add_node("human_review", human_review_node)

        # Define flow with conditional error handling
        workflow.add_edge(START, "idea_curator")
        workflow.add_conditional_edges(
            "idea_curator",
            self._should_continue_after_curator,
            {"continue": "spec_writer", "end": END},
        )
        workflow.add_conditional_edges(
            "spec_writer",
            self._should_continue_after_spec_writer,
            {"continue": "evaluator", "end": END},
        )
        workflow.add_conditional_edges(
            "evaluator",
            self._should_continue_after_evaluator,
            {"continue": "human_review", "end": END},
        )
        workflow.add_conditional_edges(
            "human_review",
            self._should_continue_after_review,
            {"continue": END, "revise": "spec_writer", "end": END},
        )

        return workflow.compile(checkpointer=self.checkpointer, interrupt_before=["human_review"])

    def _should_continue_after_curator(self, state: WorkflowState) -> str:
        """Determine if workflow should continue after idea curator."""
        error = state.get("error", "")
        if error and error.strip():
            return "end"
        return "continue"

    def _should_continue_after_spec_writer(self, state: WorkflowState) -> str:
        """Determine if workflow should continue after spec writer."""
        error = state.get("error", "")
        if error and error.strip():
            return "end"
        return "continue"

    def _should_continue_after_evaluator(self, state: WorkflowState) -> str:
        """Determine if workflow should continue after evaluator."""
        error = state.get("error", "")
        if error and error.strip():
            return "end"

        # Check if evaluation resulted in NO_GO
        evaluation_results = state.get("evaluation_results", {})
        if evaluation_results.get("go_no_go") == "NO_GO":
            return "end"

        return "continue"

    def _should_continue_after_review(self, state: WorkflowState) -> str:
        """Determine workflow direction after human review."""
        current_phase = state.get("current_phase", "")

        if current_phase == "approved":
            return "continue"
        elif current_phase == "revision_requested":
            return "revise"
        else:  # rejected or error
            return "end"

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

    async def spec_writer_node(self, state: WorkflowState) -> dict[str, Any]:
        """Generate technical specification from curated idea."""
        try:
            # Use curation result from previous agent
            curation_result = state.get("product_idea", {})
            if not curation_result:
                raise ValueError("No curation result available from idea curator")

            result = await self.spec_writer.process({"curation_result": curation_result})

            return {
                "technical_spec": result["technical_spec"],
                "current_phase": "specified",
                "error": "",
            }
        except Exception as e:
            return {
                "error": str(e),
                "current_phase": "error",
            }

    async def evaluator_node(self, state: WorkflowState) -> dict[str, Any]:
        """Evaluate technical specification for feasibility and risk."""
        try:
            # Use technical spec from previous agent
            technical_spec = state.get("technical_spec", {})
            if not technical_spec:
                raise ValueError("No technical specification available from spec writer")

            result = await self.evaluator.process({"technical_spec": technical_spec})

            return {
                "evaluation_results": result["evaluation_results"],
                "current_phase": "evaluated",
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
