"""AI Work OS — production FastAPI application.

Exposes REST API + PWA static frontend. Tuned for free-tier hosts
(Render) with single-worker gunicorn and ephemeral disk.
"""
from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.agents.custom_agent import CustomAgent
from src.agents.specialist_agents import (
    AnalystAgent,
    DeveloperAgent,
    ExecutiveAssistantAgent,
    ResearchAgent,
    WriterAgent,
)
from src.core.ai_manager import AIManager
from src.core.llm_client import LLMClient, LLMError
from src.core.memory import WorkMemory
from src.core.work_graph import WorkGraph, WorkNode
from src.permissions.permission_manager import PermissionManager
from src.verification.verifier import Verifier

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("ai_work_os")

STATIC_DIR = Path(__file__).parent / "static"
VERSION = "2.0.0"


class ChatRequest(BaseModel):

    message: str = Field(..., min_length=1, max_length=16000)

    system_prompt: Optional[str] = Field(None, max_length=8000)

    # Work OS permanent brand behavior
    brand_prompt: str = """
You are Work OS, the AI assistant built into the Work OS platform.

IDENTITY:
- Your name is Work OS.
- Never introduce yourself as Nemotron, NVIDIA, DeepSeek, Llama, Qwen, Gemini, or any other underlying model.
- Do not mention the underlying AI model or provider unless the user explicitly asks about the technology powering you.
- Never pretend to be human.

PERSONALITY:
- Professional, intelligent, calm, and approachable.
- Friendly without being overly enthusiastic.
- Confident but not arrogant.
- Natural and conversational rather than robotic.
- Clear and concise by default.
- Give more detail when the user needs it.

COMMUNICATION:
- Understand the user's intent before answering.
- Give practical and actionable answers.
- Use numbered steps when explaining procedures.
- Use headings and bullet points when they improve clarity.
- Ask questions only when necessary information is missing.
- Do not repeat information unnecessarily.
- Correct mistakes politely.
- Never invent information. If uncertain, say so.

WORK OS ROLE:
- Act as a reliable digital work and productivity assistant.
- Help users organize tasks, plan work, solve problems, understand information, and make decisions.
- Turn vague requests into clear, actionable solutions when appropriate.
- Prioritize usefulness, accuracy, clarity, and efficiency.

BRAND:
- Represent Work OS professionally.
- Keep the Work OS identity consistent.
- Do not advertise or promote the underlying model or AI provider.
- If asked "Who are you?", answer naturally:
  "I'm Work OS, your AI productivity assistant."

ACCURACY:
- Do not claim to have performed actions you did not perform.
- Clearly distinguish facts from assumptions and suggestions.
- If you don't know something, say that you don't know.

Your goal is to make every interaction feel like the user is working with a professional AI assistant built into Work OS.
"""

class GoalRequest(BaseModel):
    goal: str = Field(..., min_length=1, max_length=8000)


class MemoryRequest(BaseModel):
    key: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=16000)
    category: str = Field("preference", max_length=64)
    tags: List[str] = Field(default_factory=list)
    source: str = Field("user", max_length=64)


class GraphNodeRequest(BaseModel):
    node_id: str = Field(..., min_length=1, max_length=200)
    node_type: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=500)
    properties: dict = Field(default_factory=dict)


class GraphRelationRequest(BaseModel):
    source_id: str = Field(..., min_length=1, max_length=200)
    target_id: str = Field(..., min_length=1, max_length=200)
    relation_type: str = Field(..., min_length=1, max_length=64)


class Message(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)


class AppState:
    """Long-lived runtime objects (one process = one state)."""

    def __init__(self) -> None:
        # Prefer DATA_DIR in production; fall back to class defaults so tests
        # can isolate storage via conftest monkeypatch of default_db_path.
        data_dir_env = os.getenv("DATA_DIR")
        if data_dir_env:
            data_dir = Path(data_dir_env)
            data_dir.mkdir(parents=True, exist_ok=True)
            self.memory = WorkMemory(db_path=str(data_dir / "memory.json"))
            self.work_graph = WorkGraph(db_path=str(data_dir / "work_graph.json"))
        else:
            data_dir = ROOT / "data"
            self.memory = WorkMemory()
            self.work_graph = WorkGraph()

        self.permissions = PermissionManager()
        self.verifier = Verifier()
        self.llm = LLMClient()
        self.work_graph.set_llm(self.llm)

        self.manager = AIManager(
            llm=self.llm,
            memory=self.memory,
            work_graph=self.work_graph,
            verifier=self.verifier,
            permissions=self.permissions,
        )
        self._register_agents()
        logger.info(
            "AppState ready | llm_configured=%s agents=%s data_dir=%s",
            self.llm.is_configured(),
            list(self.manager.agent_registry.keys()),
            data_dir,
        )

    def _register_agents(self) -> None:
        pairs = [
            ("research", ResearchAgent),
            ("analyst", AnalystAgent),
            ("writer", WriterAgent),
            ("developer", DeveloperAgent),
            ("executive_assistant", ExecutiveAssistantAgent),
            ("custom", CustomAgent),
        ]
        for key, cls in pairs:
            self.manager.register_agent(key, cls(llm=self.llm))


state: Optional[AppState] = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global state
    state = AppState()
    yield
    logger.info("Shutting down AI Work OS")


app = FastAPI(
    title="AI Work OS",
    version=VERSION,
    description="AI-native multi-agent work operating system",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _require_state() -> AppState:
    global state
    if state is None:
        state = AppState()
    return state


def _plan_to_dict(plan: Any) -> dict:
    if hasattr(plan, "to_dict"):
        return plan.to_dict()
    if isinstance(plan, dict):
        return plan
    return {"goal": getattr(plan, "goal", ""), "status": "unknown", "tasks": []}


@app.get("/api/health")
def health():
    st = _require_state()
    return {
        "status": "ok",
        "version": VERSION,
        "configured": st.llm.is_configured(),
        "model": st.llm.model,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "agents": len(st.manager.agent_registry),
    }


@app.get("/api/models")
def list_models():
    """Curated OpenRouter models that work with this app.

    Free-tier (":free") models cost nothing but are rate-limited; paid models
    give higher limits. Change the active model with the OPENROUTER_MODEL env
    var — no code edit or redeploy required, just restart.
    """
    st = _require_state()
    free = [
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-chat-v3.1:free",
        "qwen/qwen3-coder:free",
        "google/gemma-3-27b-it:free",
    ]
    paid = [
        "openai/gpt-4o-mini",
        "anthropic/claude-3.5-haiku",
        "google/gemini-2.0-flash-001",
    ]
    return {
        "active_model": st.llm.model,
        "configured": st.llm.is_configured(),
        "free": free,
        "paid": paid,
    }


@app.get("/api/agents")
def agents():
    st = _require_state()
    return {
        "agents": [
            {
                "type": key,
                "name": agent.name,
                "description": getattr(agent, "description", ""),
                "capabilities": list(getattr(agent, "capabilities", []) or []),
            }
            for key, agent in st.manager.agent_registry.items()
        ]
    }


@app.post("/api/chat")
def chat(req: ChatRequest):
    st = _require_state()
    if not st.llm.is_configured():
        raise HTTPException(
            503,
            "OPENROUTER_API_KEY is not set. Add it in Render Environment (or .env locally).",
        )
    try:
        response = st.llm.chat(
            [{"role": "user", "content": req.message}],
            system_prompt=req.system_prompt,
        )
        return {"response": response, "reply": response}
    except LLMError as e:
        logger.error("Chat LLM error: %s", e)
        raise HTTPException(502, str(e)) from e
    except Exception as e:
        logger.exception("Chat error")
        raise HTTPException(500, str(e)) from e


@app.post("/api/plan")
def plan(req: GoalRequest):
    st = _require_state()
    try:
        result = st.manager.create_plan(req.goal)
        return _plan_to_dict(result)
    except Exception as e:
        logger.exception("Plan error")
        raise HTTPException(500, str(e)) from e


@app.post("/api/execute")
def execute(req: GoalRequest):
    st = _require_state()
    try:
        plan_obj = st.manager.create_plan(req.goal)
        result = st.manager.execute_plan(plan_obj)
        return result
    except Exception as e:
        logger.exception("Execute error")
        raise HTTPException(500, str(e)) from e


@app.get("/api/memory")
def get_memory():
    st = _require_state()
    items = st.memory.get_all()
    return {
        "items": [
            item.to_dict() if hasattr(item, "to_dict") else item for item in items
        ]
    }


@app.post("/api/memory")
def add_memory(req: MemoryRequest):
    st = _require_state()
    st.memory.remember(
        key=req.key,
        content=req.content,
        category=req.category,
        tags=req.tags,
        source=req.source,
    )
    return {"status": "ok"}


@app.delete("/api/memory/{key}")
def delete_memory(key: str):
    st = _require_state()
    st.memory.forget(key)
    return {"status": "ok"}


@app.post("/api/graph/node")
def add_graph_node(req: GraphNodeRequest):
    st = _require_state()
    node = WorkNode(
        node_id=req.node_id,
        node_type=req.node_type,
        name=req.name,
        properties=req.properties,
    )
    st.work_graph.add_node(node)
    return {"status": "ok"}


@app.post("/api/graph/relation")
def add_graph_relation(req: GraphRelationRequest):
    st = _require_state()
    st.work_graph.add_relation(
        source_id=req.source_id,
        target_id=req.target_id,
        relation_type=req.relation_type,
    )
    return {"status": "ok"}


@app.post("/api/graph/query")
def query_graph(req: Message):
    st = _require_state()
    try:
        result = st.work_graph.query(req.message)
        return {"result": result}
    except Exception as e:
        logger.exception("Graph query error")
        raise HTTPException(500, str(e)) from e


if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def root():
    index = STATIC_DIR / "index.html"
    if not index.exists():
        raise HTTPException(404, "Frontend not found")
    return FileResponse(index, media_type="text/html")


@app.get("/app.js")
def app_js():
    path = STATIC_DIR / "app.js"
    if not path.exists():
        raise HTTPException(404, "app.js not found")
    return FileResponse(path, media_type="application/javascript")


@app.get("/sw.js")
def sw_js():
    path = STATIC_DIR / "sw.js"
    if not path.exists():
        raise HTTPException(404, "sw.js not found")
    return FileResponse(
        path,
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache"},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, (StarletteHTTPException, HTTPException, RequestValidationError)):
        raise exc
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "path": str(request.url.path)},
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.server:app", host="0.0.0.0", port=port, reload=False)
