"""Tests for the LLM Client and AI planning.

To test no-key behavior, we directly create clients with api_key=None
since pydantic v2 settings may cache .env values.
"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from src.core.ai_manager import AIManager
from src.core.llm_client import LLMClient, LLMError


class TestLLMClient:
    def test_not_configured_without_key(self):
        """Without an API key, the client must refuse to call the AI."""
        client = LLMClient(api_key=None)
        assert client.is_configured() is False

    def test_configured_with_key(self):
        """With a key, the client should be ready."""
        client = LLMClient(api_key="sk-or-test")
        assert client.is_configured() is True

    def test_chat_raises_without_key(self):
        """Calling chat() without a key must raise a helpful error."""
        client = LLMClient(api_key=None)
        with pytest.raises(RuntimeError) as excinfo:
            client.chat(messages=[{"role": "user", "content": "hi"}])
        assert "OPENROUTER_API_KEY" in str(excinfo.value)

    def test_model_defaults_to_settings(self):
        """No explicit model should resolve to the env-driven settings model."""
        from config.settings import settings
        client = LLMClient(api_key=None)
        assert client.model == settings.openrouter_model

    def test_explicit_model_overrides_settings(self):
        """An explicit model arg must win over the settings default."""
        client = LLMClient(api_key=None, model="openai/gpt-4o-mini")
        assert client.model == "openai/gpt-4o-mini"

    def test_sampling_params_from_settings(self):
        """temperature / max_tokens should come from settings when not given."""
        from config.settings import settings
        client = LLMClient(api_key=None)
        assert client.temperature == settings.ai_temperature
        assert client.max_tokens == settings.ai_max_tokens
class _FakeLLM:
    """A fake LLM that returns a canned JSON plan (no internet needed)."""
    def __init__(self, reply: str):
        self._reply = reply

    def is_configured(self) -> bool:
        return True

    def chat(self, messages, system_prompt=None, temperature=None, max_tokens=None) -> str:
        return self._reply


class TestAIPlanning:
    def test_parse_valid_json_plan(self):
        manager = AIManager(llm=_FakeLLM(
            '[{"id": "t1", "description": "Research", "agent": "research", "depends_on": []}]'
        ))
        tasks = manager._parse_tasks(
            '[{"id": "t1", "description": "Research", "agent": "research", "depends_on": []}]'
        )
        assert len(tasks) == 1
        assert tasks[0]["agent"] == "research"

    def test_parse_code_fenced_json(self):
        manager = AIManager(llm=_FakeLLM(""))
        tasks = manager._parse_tasks(
            '```json\n[{"id": "t1", "description": "x", "agent": "writer", "depends_on": []}]\n```'
        )
        assert len(tasks) == 1
        assert tasks[0]["agent"] == "writer"

    def test_parse_invalid_json_returns_empty(self):
        manager = AIManager(llm=_FakeLLM(""))
        assert manager._parse_tasks("not json at all") == []

    def test_create_plan_with_llm_builds_tasks(self):
        fake = _FakeLLM(
            '[{"id": "t1", "description": "Research", "agent": "research", "depends_on": []},'
            '{"id": "t2", "description": "Write report", "agent": "writer", "depends_on": ["t1"]}]'
        )
        manager = AIManager(llm=fake)
        plan = manager.create_plan("Write a report about the market")
        assert len(plan.tasks) == 2
        assert plan.tasks[0].agent_type == "research"
        assert plan.tasks[1].depends_on == ["t1"]

    def test_create_plan_empty_without_key(self):
        manager = AIManager(llm=LLMClient(api_key=None))
        plan = manager.create_plan("Anything")
        assert len(plan.tasks) == 0