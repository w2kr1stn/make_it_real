"""tech stack review agent."""

from .requirements_review_agent import RequirementsReviewAgent

class TaskReviewAgent(RequirementsReviewAgent):
    """Agent responsible for reviewing the task list."""

    def _kind(self) -> str:
        return "task list items"
