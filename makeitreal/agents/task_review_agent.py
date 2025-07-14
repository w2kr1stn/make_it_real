"""task list review agent."""

from .requirements_review_agent import RequirementsReviewAgent


class TaskReviewAgent(RequirementsReviewAgent):
    """Agent responsible for reviewing the task list."""

    def __init__(self) -> None:
        """Initialize agent."""
        super().__init__(proposal_key="tasks", kind="tasks")
