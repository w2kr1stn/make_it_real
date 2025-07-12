"""State definition for LangGraph workflow."""

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class WorkflowState(TypedDict):
    """State schema for the ideation workflow."""

    messages: Annotated[list[BaseMessage], add_messages]
    idea: BaseMessage
    features : list[str]
    featureListApproved: bool
    techStack: list[str]
    techStackApproved: bool
    changeRequest: str
    tasks: list[str]
    error: str