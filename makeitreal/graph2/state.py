"""State definition for LangGraph workflow."""

from typing import Annotated, TypedDict
from pydantic import BaseModel

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class Proposal(BaseModel):
    """A set of proposed items that is subject to review."""

    proposedItems: list[str] = []
    changeRequest: str|None = None
    agentApproved: bool = False
    humanApproved: bool = False


class WorkflowState(TypedDict):
    """State schema for the ideation workflow."""

    messages: Annotated[list[BaseMessage], add_messages]
    idea: BaseMessage
    features : Proposal
    techStack: Proposal
    tasks: Proposal
    phase: str
