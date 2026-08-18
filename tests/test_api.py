"""
API tests for AI Work OS FastAPI server.

Uses FastAPI TestClient for in-process testing without network calls.
These tests verify the actual HTTP contract of every endpoint.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Create a TestClient for the FastAPI app.

    Tests must be hermetic: we force the app's LLM to an unconfigured client
    so no test ever depends on the network, a live API key, or OpenRouter
    rate limits. Endpoints then exercise their real code paths (chat -> 503,
    plan -> empty plan) deterministically.
    """
    from src.core.llm_client import LLMClient
    import app.server as server

    # Context manager form runs the lifespan (creates server.state) so we can
    # swap in an offline LLM before any request handler runs.
    with TestClient(server.app) as c:
        if server.state is not None:
            offline = LLMClient(api_key=None)
            server.state.llm = offline
            server.state.manager.llm = offline
            server.state.work_graph.set_llm(offline)
        yield c


class TestHealthEndpoint:
    """Test /api/health endpoint."""

    def test_health_returns_ok(self, client):
        """Health endpoint should return status ok."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "configured" in data
        assert isinstance(data["configured"], bool)

    def test_health_includes_model(self, client):
        """Health should expose the active model for observability."""
        response = client.get("/api/health")
        data = response.json()
        assert "model" in data
        assert isinstance(data["model"], str)
        assert data["model"] != ""


class TestModelsEndpoint:
    """Test /api/models curated model list."""

    def test_models_endpoint(self, client):
        """Should return active model and curated free/paid lists."""
        response = client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert "active_model" in data
        assert "free" in data
        assert "paid" in data
        assert isinstance(data["free"], list)
        assert isinstance(data["paid"], list)
        # All curated free models must use the :free suffix
        for m in data["free"]:
            assert m.endswith(":free")


class TestAgentsEndpoint:
    """Test /api/agents endpoint."""

    def test_list_agents(self, client):
        """Should return list of registered agents."""
        response = client.get("/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert isinstance(data["agents"], list)
        assert len(data["agents"]) >= 5

    def test_agent_structure(self, client):
        """Each agent should have type, name, and capabilities."""
        response = client.get("/api/agents")
        agents = response.json()["agents"]
        for agent in agents:
            assert "type" in agent
            assert "name" in agent
            assert "capabilities" in agent
            assert isinstance(agent["capabilities"], list)


class TestChatEndpoint:
    """Test /api/chat endpoint."""

    def test_chat_requires_message(self, client):
        """Chat endpoint should require message field."""
        response = client.post("/api/chat", json={})
        assert response.status_code == 422

    def test_chat_valid_request(self, client):
        """Chat should accept valid request (may fail if no API key or LLM error)."""
        response = client.post("/api/chat", json={"message": "hello"})
        # May succeed, or return 503 (no key), 500 (LLM error), or 502 (API call failed)
        assert response.status_code in [200, 500, 502, 503]

    def test_chat_with_system_prompt(self, client):
        """Chat should accept optional system_prompt."""
        response = client.post(
            "/api/chat",
            json={"message": "hello", "system_prompt": "You are helpful"}
        )
        # May succeed, or return error codes
        assert response.status_code in [200, 500, 502, 503]


class TestPlanEndpoint:
    """Test /api/plan endpoint."""

    def test_plan_requires_goal(self, client):
        """Plan endpoint should require goal field."""
        response = client.post("/api/plan", json={})
        assert response.status_code == 422

    def test_plan_valid_request(self, client):
        """Plan should create execution plan for goal."""
        response = client.post("/api/plan", json={"goal": "Write a report"})
        assert response.status_code == 200
        data = response.json()
        assert "goal" in data
        assert "status" in data
        assert "tasks" in data
        assert isinstance(data["tasks"], list)


class TestExecuteEndpoint:
    """Test /api/execute endpoint."""

    def test_execute_requires_goal(self, client):
        """Execute endpoint should require goal field."""
        response = client.post("/api/execute", json={})
        assert response.status_code == 422


class TestMemoryEndpoints:
    """Test /api/memory endpoints."""

    def test_get_memory(self, client):
        """Should return memory items list."""
        response = client.get("/api/memory")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_add_memory(self, client):
        """Should add memory and return ok."""
        response = client.post(
            "/api/memory",
            json={
                "key": "test_key",
                "content": "Test content",
                "category": "preference"
            }
        )
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_delete_memory(self, client):
        """Should delete memory and return ok."""
        client.post(
            "/api/memory",
            json={"key": "delete_me", "content": "temp", "category": "test"}
        )
        response = client.delete("/api/memory/delete_me")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestGraphEndpoints:
    """Test /api/graph endpoints."""

    def test_add_graph_node(self, client):
        """Should add node to work graph."""
        response = client.post(
            "/api/graph/node",
            json={
                "node_id": "proj1",
                "node_type": "project",
                "name": "Test Project",
                "properties": {"priority": "high"}
            }
        )
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_add_graph_relation(self, client):
        """Should add relation between nodes."""
        client.post(
            "/api/graph/node",
            json={"node_id": "p1", "node_type": "person", "name": "A", "properties": {}}
        )
        client.post(
            "/api/graph/node",
            json={"node_id": "t1", "node_type": "project", "name": "B", "properties": {}}
        )
        response = client.post(
            "/api/graph/relation",
            json={"source_id": "p1", "target_id": "t1", "relation_type": "manages"}
        )
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_query_graph(self, client):
        """Should query work graph."""
        response = client.post(
            "/api/graph/query",
            json={"message": "What projects exist?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data


class TestStaticFiles:
    """Test static file serving."""

    def test_root_serves_index(self, client):
        """Root should serve index.html."""
        response = client.get("/")
        assert response.status_code == 200
        assert "html" in response.headers["content-type"].lower()

    def test_app_js_served(self, client):
        """app.js should be served."""
        response = client.get("/app.js")
        assert response.status_code == 200

    def test_sw_js_served(self, client):
        """sw.js should be served."""
        response = client.get("/sw.js")
        assert response.status_code == 200


class TestCORSHeaders:
    """Test CORS middleware."""

    def test_cors_headers_present(self, client):
        """CORS headers should be present in responses."""
        response = client.options(
            "/api/chat",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        assert "access-control-allow-origin" in response.headers

    def test_execute_valid_request(self, client):
        """Execute should process goal and return result."""
        response = client.post(
            "/api/execute",
            json={"goal": "Research Python best practices"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data