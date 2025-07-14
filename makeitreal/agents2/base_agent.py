"""Base agent class for all MakeItReal agents."""

from abc import ABC, abstractmethod
from typing import Any
from ..graph2.state import Proposal

class BaseAgent(ABC):
    """Abstract agent base class for all agents in the MakeItReal system."""

    def __init__(self, name: str) -> None:
        """Initialize agent with a name.

        Args:
            name: Human-readable name for the agent
        """
        self.name = name

    @abstractmethod
    async def process(self, proposal: Proposal, idea:str) -> dict[str, Any]:
        """Process input data and return structured output.

        Args:
            input_data: Dictionary containing input data for processing

        Returns:
            Dictionary containing the agent's structured output
        """
        pass

    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}')"
