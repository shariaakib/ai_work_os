"""
Tests for AI Work OS core components.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.ai_manager import AIManager, Plan, Task, GoalStatus
from src.core.work_graph import WorkGraph, WorkNode
from src.core.memory import WorkMemory
from src.agents.base_agent import BaseAgent
from src.agents.specialist_agents import ResearchAgent, WriterAgent
from src.permissions.permission_manager import PermissionManager, Action, PermissionLevel
from src.verification.verifier import Verifier


class TestAIManager:
    def test_create_plan(self):
        manager = AIManager()
        plan = manager.create_plan("Write a report")
        assert plan.goal == "Write a report"
        assert plan.status == GoalStatus.PLANNING

    def test_register_and_execute(self):
        manager = AIManager()
        manager.register_agent("test_agent", ResearchAgent())
        plan = Plan("Test goal")
        plan.add_task(Task("task-1", "Research topic", "test_agent"))
        result = manager.execute_plan(plan)
        assert result["status"] == "completed"


class TestWorkGraph:
    def test_add_node(self):
        graph = WorkGraph()
        node = WorkNode("proj-1", "project", "Test Project")
        graph.add_node(node)
        assert "proj-1" in graph.nodes
        assert graph.nodes["proj-1"].name == "Test Project"

    def test_add_relation(self):
        graph = WorkGraph()
        graph.add_node(WorkNode("p1", "person", "Alice"))
        graph.add_node(WorkNode("p2", "project", "Project X"))
        graph.add_relation("p1", "p2", "manages")
        related = graph.get_related("p1", "manages")
        assert len(related) == 1
        assert related[0].name == "Project X"


class TestWorkMemory:
    def test_remember_and_recall(self):
        memory = WorkMemory()
        memory.remember("email_style", "Keep emails short")
        result = memory.recall("email_style")
        assert result == "Keep emails short"

    def test_forget(self):
        memory = WorkMemory()
        memory.remember("test_key", "test value")
        memory.forget("test_key")
        assert memory.recall("test_key") is None

    def test_search(self):
        memory = WorkMemory()
        memory.remember("pref1", "I like short meetings", tags=["meetings"])
        results = memory.search("short meetings")
        assert len(results) == 1


class TestPermissionManager:
    def test_classify_safe(self):
        pm = PermissionManager()
        level = pm.classify_action("read", "Read a document")
        assert level == PermissionLevel.SAFE

    def test_classify_high_risk(self):
        pm = PermissionManager()
        level = pm.classify_action("delete", "Delete file permanently")
        assert level == PermissionLevel.HIGH_RISK

    def test_classify_approval(self):
        pm = PermissionManager()
        level = pm.classify_action("send", "Send an email")
        assert level == PermissionLevel.APPROVAL

    def test_approval_flow(self):
        pm = PermissionManager()
        action = Action("send", "Send email", PermissionLevel.APPROVAL)
        assert pm.can_execute(action) is False
        pm.request_approval(action)
        pm.approve(action)
        assert action.is_approved is True


class TestVerifier:
    def test_verify_valid_output(self):
        verifier = Verifier()
        result = verifier.verify("Some valid output text")
        assert result.passed is True
        assert result.score == 1.0

    def test_verify_none(self):
        verifier = Verifier()
        result = verifier.verify(None)
        assert result.passed is False
        assert result.score == 0.0


class TestSpecialistAgents:
    def test_research_agent(self):
        agent = ResearchAgent()
        assert agent.name == "Research"
        result = agent.execute("Test research task")
        assert result["agent"] == "research"

    def test_writer_agent(self):
        agent = WriterAgent()
        assert "report_writing" in agent.capabilities
        result = agent.execute("Write a report")
        assert result["agent"] == "writer"