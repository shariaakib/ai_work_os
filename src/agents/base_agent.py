"""
Base Agent - Abstract base class for all specialist agents.

All agents inherit from this base and implement the execute method.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseAgent(ABC):
    """Abstract base class for all specialist AI agents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.capabilities: list[str] = []

    @abstractmethod
    def execute(self, task: str, context: Optional[dict] = None) -> Any:
        """
        Execute a task and return the result.

        Args:
            task: Description of the task to perform
            context: Optional context information

        Returns:
            Result of the task execution
        """
        pass

    def get_capabilities(self) -> list[str]:
        """Return list of agent capabilities."""
        return self.capabilities

    def __repr__(self):
        return f"{self.name} Agent ({self.description})"