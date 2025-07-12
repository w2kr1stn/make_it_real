"""State definition for LangGraph workflow."""

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class WorkflowState(TypedDict):
    """State schema for the ideation workflow."""

    messages: Annotated[list[BaseMessage], add_messages]
    product_idea: dict
    market_analysis: dict
    technical_spec: dict
    evaluation_results: dict
    current_phase: str
    error: str
    requires_human_review: bool
