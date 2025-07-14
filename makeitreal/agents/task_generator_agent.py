"""tech stack generator agent."""

from .requirements_generator_agent import RequirementsGeneratorAgent

class TaskGeneratorAgent(RequirementsGeneratorAgent):
    """Agent responsible for generating the task list."""

    def _kind(self) -> str:
        return "task list items"