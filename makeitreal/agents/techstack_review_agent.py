"""tech stack review agent."""

from makeitreal.agents.requirements_review_agent import RequirementsReviewAgent


class TechStackReviewAgent(RequirementsReviewAgent):
    """Agent responsible for reviewing the tech stack."""

    def __init__(self) -> None:
        """Initialize agent."""
        super().__init__(proposal_key="tech_stack", kind="tech stack items")
