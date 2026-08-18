"""
Base Agent - Abstract base class for all specialist agents.

All agents inherit from this base and implement the execute method.

Industrial-grade version: adds LLM integration, memory context,
and structured result formatting.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, List

from src.core.llm_client import LLMClient

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all specialist AI agents.

    Provides a shared LLM client, memory integration, and a standard
    result envelope so every agent returns consistently-shaped output.
    """

    # Default system prompt - subclasses can override or extend
    SYSTEM_PROMPT: str = (
        "You are a specialist AI agent in the AI Work OS. "
        "Complete the assigned task thoroughly and return your work."
    )

    def __init__(self, name: str, description: str, llm: Optional[LLMClient] = None):
        self.name = name
        self.description = description
        self.capabilities: List[str] = []
        self.llm = llm or LLMClient()

    @abstractmethod
    def execute(self, task: str, context: Optional[dict] = None) -> Any:
        """Execute a task and return the result.

        Args:
            task: Description of the task to perform
            context: Optional context information

        Returns:
            Result of the task execution
        """
        pass

    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        return self.capabilities

    def _llm_call(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Make an LLM call with error handling, falling back gracefully.

        Args:
            prompt: The user prompt to send to the LLM.
            system_prompt: Optional system prompt override.
            temperature: Optional temperature override.

        Returns:
            The LLM response text, or an error placeholder if the call fails.
        """
        if not self.llm.is_configured():
            return f"[LLM not configured] {self.name} cannot complete this task. " \
                   f"Set OPENROUTER_API_KEY in .env"

        try:
            return self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=system_prompt or self.SYSTEM_PROMPT,
                temperature=temperature,
            )
        except Exception as e:
            logger.error("%s LLM call failed: %s", self.name, str(e))
            return f"[LLM error in {self.name}] {str(e)}"

    def _build_result(
        self,
        task: str,
        content: str,
        status: str = "completed",
        extra: Optional[dict] = None,
    ) -> dict:
        """Build a standard result envelope.

        Args:
            task: The task description that was executed.
            content: The main output content from the agent.
            status: Execution status (completed, pending, error).
            extra: Optional additional fields to include.

        Returns:
            A standardized result dictionary.
        """
        result: dict = {
            "agent": self.name.lower(),
            "task": task,
            "status": status,
            "content": content,
        }
        if extra:
            result.update(extra)
        return result

    def __repr__(self):
        return f"{self.name} Agent ({self.description})"