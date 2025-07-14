"""State definition for LangGraph workflow."""

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel


class Proposal(BaseModel):
    """A set of proposed items that is subject to review."""

    proposed_items: list[str] = []
    change_request: str | None = None
    agent_approved: bool = False
    human_approved: bool = False


class WorkflowState(TypedDict):
    """State schema for the ideation workflow."""

    messages: Annotated[list[BaseMessage], add_messages]
    idea: BaseMessage
    features: Proposal
    tech_stack: Proposal
    tasks: Proposal
