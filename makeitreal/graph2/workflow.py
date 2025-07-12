"""LangGraph workflow implementation for idea processing."""

import uuid
from random import randint
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from ..agents.evaluator import Evaluator
from ..agents.idea_curator import IdeaCurator
from ..agents.spec_writer import SpecWriter
from .human_review import human_review_node,human_review_features_node,human_review_techstack_node
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
        workflow.add_node("requirements_agent", self.idea_curator_node)
        #TODO:add agent
        workflow.add_node("requirements_review", self.requirements_review_node)
        workflow.add_node("human_review_features", human_review_features_node)
        workflow.add_node("human_review_techStack", human_review_techstack_node)

        # Define flow with conditional error handling
        workflow.add_edge(START, "requirements_agent")
        workflow.add_conditional_edges(
            "requirements_agent",
            self._should_continue_after_curator,
            {"review":"requirements_review" ,
             "end": END},
        )

        workflow.add_conditional_edges(
            "requirements_review",
            self._should_continue_after_requirements_review,
            {"review":"human_review_features" ,
             "change": "requirements_agent",
             "end": END},
        )

        return workflow.compile(checkpointer=self.checkpointer) #

    def _should_continue_after_curator(self, state: WorkflowState) -> str:
        """Determine if workflow should continue after idea curator."""
        error = state.get("error", "")
        print("should continue after curator")
        if error and error.strip():
            return "end"
        return "review"

    def _should_continue_after_requirements_review(self, state: WorkflowState) -> str:
        """Determine if workflow should continue after the requirements are reviewed."""
        error = state.get("error", "")
        changeRequest = state.get("changeRequest")
        print("should continue after review: "+changeRequest)
        if error and error.strip():
            return "end"

        if changeRequest:
            return "change"

        return "review"

    async def idea_curator_node(self, state: WorkflowState) -> dict[str, Any]:
        """Process idea with curator agent."""
        try:
            # Extract idea from the last message
            # idea = state["idea"]

            # result = await self.idea_curator.process(state)

            return {
                "features": [
                    "Feature 1",
                    "Feature 2",
                    "Feature 3",
                    "Feature 4",
                    "Feature 5",
                ],
                "error": "",
            }
        except Exception as e:
            return {
                "error": str(e),
                "current_phase": "error",
            }


    async def requirements_review_node(self, state: WorkflowState) -> dict[str, Any]:
        """Process idea with curator agent."""
        try:

            print("reuirements_review_node")
            app = True
            cr = ""
            if randint(1,100) > 50:
                app = False
                cr = "change me"

            return {
                "changeRequest": cr,
                "featureListApproved" : app,
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
            #TODO: check if props can be accessed directly
            "messages": [HumanMessage(content=idea)],
            "idea": HumanMessage(content=idea),
            "features": [],
            "featureListApproved": False,
            "techStack": [],
            "techStackApproved": False,
            "changeRequest": None,
            "tasks": []
        }
        config = {"configurable": {"thread_id": thread_id}}
        result = await self.graph.ainvoke(initial_state, config)

        return result
