"""tech stack review agent."""

from .requirements_review_agent import RequirementsReviewAgent


class TechStackReviewAgent(RequirementsReviewAgent):
    """Agent responsible for reviewing the tech stack."""

    def _kind(self) -> str:
        return "tech stack items"
