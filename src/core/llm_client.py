"""LLM Client - Talks to AI models through OpenRouter.

Production-ready: retries, timeouts, error handling, streaming."""
import logging, time
from typing import List, Optional
from openai import OpenAI, OpenAIError
from config.settings import settings

logger = logging.getLogger(__name__)
_SENTINEL = object()


class LLMError(Exception):
    """Custom exception for LLM errors."""
    pass


class LLMClient:
    """Wrapper around OpenRouter API. api_key=None disables calls."""

    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    DEFAULT_TIMEOUT: float = 30.0

    def __init__(
        self,
        api_key=_SENTINEL,
        base_url=settings.openrouter_base_url,
        model=None,
        temperature=None,
        max_tokens=None,
        timeout=None,
    ):
        self.api_key = (
            settings.effective_api_key if api_key is _SENTINEL else api_key
        )
        self.base_url = base_url
        # Model / sampling fall back to env-driven settings so a single
        # OPENROUTER_MODEL / AI_TEMPERATURE / AI_MAX_TOKENS change in .env or
        # the host (Render) is all that's needed — no code edit.
        self.model = model or settings.openrouter_model
        self.temperature = (
            settings.ai_temperature if temperature is None else temperature
        )
        self.max_tokens = (
            settings.ai_max_tokens if max_tokens is None else max_tokens
        )
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self._client = None
        if self.api_key:
            self._client = OpenAI(
                api_key=self.api_key, base_url=base_url, timeout=self.timeout
            )

    def is_configured(self) -> bool:
        """True if an API key is available."""
        return self._client is not None

    def chat(self, messages, system_prompt=None, temperature=None, max_tokens=None):
        """Send a conversation to the AI and return its text reply."""
        if not self.is_configured():
            raise RuntimeError("No OpenRouter API key. Set OPENROUTER_API_KEY in .env")

        full = []
        if system_prompt:
            full.append({"role": "system", "content": system_prompt})
        full.extend(messages)

        t = temperature if temperature is not None else self.temperature
        mt = max_tokens if max_tokens is not None else self.max_tokens

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                resp = self._client.chat.completions.create(
                    model=self.model, messages=full, temperature=t, max_tokens=mt
                )
                return resp.choices[0].message.content or ""
            except OpenAIError as e:
                logger.warning("LLM retry %d/%d: %s", attempt, self.MAX_RETRIES, e)
                if attempt == self.MAX_RETRIES:
                    raise LLMError(
                        f"LLM failed after {self.MAX_RETRIES} attempts: {e}"
                    ) from e
                time.sleep(self.RETRY_DELAY * (2 ** (attempt - 1)))

        raise LLMError(f"LLM failed after {self.MAX_RETRIES} attempts")

    def chat_stream(self, messages, system_prompt=None, temperature=None, max_tokens=None):
        """Stream a chat response, yielding chunks."""
        if not self.is_configured():
            raise RuntimeError("No OpenRouter API key. Set OPENROUTER_API_KEY in .env")

        full = []
        if system_prompt:
            full.append({"role": "system", "content": system_prompt})
        full.extend(messages)

        t = temperature if temperature is not None else self.temperature
        mt = max_tokens if max_tokens is not None else self.max_tokens

        resp = self._client.chat.completions.create(
            model=self.model, messages=full, temperature=t, max_tokens=mt, stream=True
        )
        for chunk in resp:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content