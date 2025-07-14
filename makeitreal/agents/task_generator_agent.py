"""task list generator agent."""

from .requirements_generator_agent import RequirementsGeneratorAgent
from makeitreal.graph.state import WorkflowState

class TaskGeneratorAgent(RequirementsGeneratorAgent):
    """Agent responsible for generating the task list."""

    def __init__(self) -> None:
        """Initialize agent."""
        super().__init__(proposal_key="tasks", kind="tasks")

    def _build_human_prompt(self) -> str:
        return """I have the following idea:
                  {idea}

                  The idea includes the following use-cases:
                  {features}

                  The project should be implemented using the following tech stack:
                  {tech_stack}

                  Based on the idea, use-cases and tech stack, the following tasks were derived:
                  {items}

                  I want to change the task list as follows:
                  {change_request}

                  Please propose a list of tasks to cover all the mentioned features, taking the given tech stack into account!
                  """

    def _additional_variables(self, state: WorkflowState) -> dict[str, str]:
        features = state.get("features")
        tech_stack = state.get("tech_stack")

        return {
            "features": self._items2str(features.proposed_items),
            "tech_stack": self._items2str(tech_stack.proposed_items),
        }
