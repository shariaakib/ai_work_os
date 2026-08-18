"""Tests for AI Work OS core components - industrial-grade coverage."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.ai_manager import AIManager, Plan, Task, GoalStatus
from src.core.llm_client import LLMClient
from src.core.work_graph import WorkGraph, WorkNode
from src.core.memory import WorkMemory
from src.permissions.permission_manager import PermissionManager, Action, PermissionLevel
from src.verification.verifier import Verifier

# Shared unconfigured LLM - no real API calls
_no_llm = LLMClient(api_key=None)


class TestAIManager:
    def test_create_plan(self):
        manager = AIManager(llm=_no_llm)
        plan = manager.create_plan("Write a report")
        assert plan.goal == "Write a report"
        assert plan.status == GoalStatus.PLANNING

    def test_empty_plan_without_key(self):
        manager = AIManager(llm=_no_llm)
        plan = manager.create_plan("Anything")
        assert len(plan.tasks) == 0

    def test_register_and_execute(self):
        from src.agents.specialist_agents import ResearchAgent
        manager = AIManager(llm=_no_llm)
        manager.register_agent("test_agent", ResearchAgent(llm=_no_llm))
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

    def test_add_relation(self):
        graph = WorkGraph()
        graph.add_node(WorkNode("p1", "person", "Alice"))
        graph.add_node(WorkNode("p2", "project", "Project X"))
        graph.add_relation("p1", "p2", "manages")
        related = graph.get_related("p1", "manages")
        assert len(related) == 1

    def test_find_node_by_name(self):
        graph = WorkGraph()
        graph.add_node(WorkNode("n1", "project", "Phoenix"))
        assert graph.find_node_by_name("phoenix") is not None
        assert graph.find_node_by_name("unknown") is None

    def test_remove_node_cleans_relations(self):
        graph = WorkGraph()
        graph.add_node(WorkNode("a", "test", "A"))
        graph.add_node(WorkNode("b", "test", "B"))
        graph.add_relation("a", "b", "links")
        graph.remove_node("a")
        assert len(graph.relations) == 0


class TestWorkMemory:
    def test_remember_and_recall(self):
        memory = WorkMemory()
        memory.remember("email_style", "Keep emails short")
        assert memory.recall("email_style") == "Keep emails short"

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
        assert pm.classify_action("read", "Read a document") == PermissionLevel.SAFE

    def test_classify_high_risk(self):
        pm = PermissionManager()
        assert pm.classify_action("delete", "Delete file permanently") == PermissionLevel.HIGH_RISK

    def test_classify_approval(self):
        pm = PermissionManager()
        assert pm.classify_action("send", "Send an email") == PermissionLevel.APPROVAL

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
