"""
LLM Client - Talks to an AI model through OpenRouter.

This is the "brain connection" of the AI Work OS. Everything that needs
to speak to an AI model (planning, agents, memory, tools) goes through here.

Why OpenRouter? It gives us ONE API for many models (GPT, Claude, Gemini...),
which is what the VISION calls "model independence". We can switch the model
by changing a single string.
"""

from typing import List, Optional

from openai import OpenAI

from config.settings import settings


class LLMClient:
    """
    A thin wrapper around the OpenRouter API (OpenAI-compatible).

    Who uses it: AIManager (for planning), agents, memory, tools.
    It reads the API key from the environment (via config/settings).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = settings.openrouter_base_url,
        model: str = "openai/gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        # If no key is passed, read it from settings (which reads .env)
        self.api_key = api_key or settings.openrouter_api_key

        # No key yet? We'll fail with a clear message when asked to talk.
        self._client: Optional[OpenAI] = None
        if self.api_key:
            self._client = OpenAI(api_key=self.api_key, base_url=base_url)

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def is_configured(self) -> bool:
        """True if we have an API key (i.e. can actually call the AI)."""
        return self._client is not None

    def chat(
        self,
        messages: List[dict],
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Send a conversation to the AI and return its text reply.

        'messages' is a list of {role, content}. Roles:
          - "system": instructions for the AI
          - "user":   what the human says
          - "assistant": previous AI replies (for memory)
        """
        if not self.is_configured():
            raise RuntimeError(
                "No OpenRouter API key found. Create a .env file with "
                "OPENROUTER_API_KEY=sk-or-... (get one at https://openrouter.ai)"
            )

        # Prepend a system prompt if provided.
        full_messages: List[dict] = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        response = self._client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        # The reply lives at choices[0].message.content
        return response.choices[0].message.content or ""