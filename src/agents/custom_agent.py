"""
Custom Agent - A flexible agent for custom or experimental tasks.

This agent can be used for ad-hoc tasks that don't fit into the
specialist agent categories.
"""

import logging
from typing import Optional

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CustomAgent(BaseAgent):
    """A versatile agent for custom workflows and experimentation."""

    SYSTEM_PROMPT = (
        "You are a Custom Agent in the AI Work OS. You handle ad-hoc "
        "tasks with flexibility. Complete the assigned task to the best "
        "of your ability, providing clear and useful results."
    )

    def __init__(self, llm=None):
        super().__init__(
            name="Custom",
            description="A flexible agent for custom tasks and experimentation",
            llm=llm,
        )
        self.capabilities = ["greetings", "tasks", "custom_workflows"]

    def execute(self, task: str, context: Optional[dict] = None) -> dict:
        """Execute a task with this custom agent using LLM."""
        prompt = f"Complete the following task:\n\n{task}"
        if context:
            for key, value in context.items():
                if key not in ("name", "description"):
                    prompt += f"\n{key.replace('_', ' ').title()}: {value}"

        content = self._llm_call(prompt, temperature=0.7)
        return self._build_result(
            task=task,
            content=content,
            extra={"agent": "custom", "result": content},
        )