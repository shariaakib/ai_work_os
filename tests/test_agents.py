"""Tests for all specialist agents - comprehensive coverage.

All agents are created with api_key=None to avoid real LLM calls.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.llm_client import LLMClient
from src.agents.specialist_agents import (
    ResearchAgent,
    AnalystAgent,
    WriterAgent,
    DeveloperAgent,
    ExecutiveAssistantAgent,
)
from src.agents.custom_agent import CustomAgent
from src.agents.base_agent import BaseAgent

# Shared unconfigured LLM - no API calls
_no_llm = LLMClient(api_key=None)


class TestResearchAgent:
    def test_creation(self):
        agent = ResearchAgent(llm=_no_llm)
        assert agent.name == "Research"
        assert "web_research" in agent.capabilities

    def test_execute_without_llm(self):
        agent = ResearchAgent(llm=_no_llm)
        result = agent.execute("Research Python")
        assert result["agent"] == "research"
        assert "content" in result

    def test_execute_returns_content(self):
        agent = ResearchAgent(llm=_no_llm)
        result = agent.execute("What is Python?")
        assert "LLM not configured" in result["content"]


class TestAnalystAgent:
    def test_creation(self):
        agent = AnalystAgent(llm=_no_llm)
        assert agent.name == "Analyst"
        assert "data_analysis" in agent.capabilities

    def test_execute_without_llm(self):
        agent = AnalystAgent(llm=_no_llm)
        result = agent.execute("Analyze")
        assert result["agent"] == "analyst"


class TestWriterAgent:
    def test_creation(self):
        agent = WriterAgent(llm=_no_llm)
        assert agent.name == "Writer"
        assert "report_writing" in agent.capabilities

    def test_execute_without_llm(self):
        agent = WriterAgent(llm=_no_llm)
        result = agent.execute("Write")
        assert result["agent"] == "writer"


class TestDeveloperAgent:
    def test_creation(self):
        agent = DeveloperAgent(llm=_no_llm)
        assert agent.name == "Developer"
        assert "code_generation" in agent.capabilities

    def test_execute_without_llm(self):
        agent = DeveloperAgent(llm=_no_llm)
        result = agent.execute("Code")
        assert result["agent"] == "developer"


class TestExecutiveAssistantAgent:
    def test_creation(self):
        agent = ExecutiveAssistantAgent(llm=_no_llm)
        assert agent.name == "Executive Assistant"
        assert "meeting_management" in agent.capabilities

    def test_execute_without_llm(self):
        agent = ExecutiveAssistantAgent(llm=_no_llm)
        result = agent.execute("Schedule")
        assert result["agent"] == "executive_assistant"


class TestCustomAgent:
    def test_creation(self):
        agent = CustomAgent(llm=_no_llm)
        assert agent.name == "Custom"
        assert "custom_workflows" in agent.capabilities

    def test_execute_without_llm(self):
        agent = CustomAgent(llm=_no_llm)
        result = agent.execute("Task")
        assert result["agent"] == "custom"


class TestBaseAgent:
    def test_build_result(self):
        class DummyAgent(BaseAgent):
            def execute(self, task, context=None):
                return self._build_result(task, "test content")

        agent = DummyAgent("Test", "Testing", llm=_no_llm)
        result = agent.execute("do something")
        assert result["agent"] == "test"
        assert result["status"] == "completed"
        assert result["content"] == "test content"

    def test_llm_call_without_key(self):
        class DummyAgent(BaseAgent):
            def execute(self, task, context=None):
                return self._llm_call("prompt")
        agent = DummyAgent("Test", "Testing", llm=_no_llm)
        result = agent.execute("task")
        assert "LLM not configured" in result
