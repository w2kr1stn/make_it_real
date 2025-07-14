"""tech stack generator agent."""

from .requirements_generator_agent import RequirementsGeneratorAgent

class TechStackGeneratorAgent(RequirementsGeneratorAgent):
    """Agent responsible for generating tech stack."""

    def _kind(self) -> str:
        return "tech stack items"