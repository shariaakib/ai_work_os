import logging,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"src"))
from fastapi import FastAPI,HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional,List
from src.core.ai_manager import AIManager
from src.core.llm_client import LLMClient
from src.core.memory import WorkMemory
from src.core.work_graph import WorkGraph,WorkNode
from src.agents.specialist_agents import ResearchAgent,AnalystAgent,WriterAgent,DeveloperAgent,ExecutiveAssistantAgent
from src.agents.custom_agent import CustomAgent
from src.permissions.permission_manager import PermissionManager
from src.verification.verifier import Verifier

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

class ChatRequest(BaseModel): message:str; system_prompt:Optional[str]=None
class GoalRequest(BaseModel): goal:str
class MemoryRequest(BaseModel): key:str; content:str; category:str="preference"; tags:list=[]; source:str="user"
class GraphNodeRequest(BaseModel): node_id:str; node_type:str; name:str; properties:dict={}
class GraphRelationRequest(BaseModel): source_id:str; target_id:str; relation_type:str
class Message(BaseModel): message:str


class AppState:
    def __init__(self):
        self.memory = WorkMemory()
        self.work_graph = WorkGraph()
        self.permissions = PermissionManager()
        self.verifier = Verifier()
        self.llm = LLMClient()
        self.manager = AIManager(
            llm=self.llm,
            memory=self.memory,
            work_graph=self.work_graph,
            verifier=self.verifier,
            permissions=self.permissions
        )
        self._register_agents()
    
    def _register_agents(self):
        self.manager.register_agent("research", ResearchAgent(llm=self.llm))
        self.manager.register_agent("analyst", AnalystAgent(llm=self.llm))
        self.manager.register_agent("writer", WriterAgent(llm=self.llm))
        self.manager.register_agent("developer", DeveloperAgent(llm=self.llm))
        self.manager.register_agent("executive_assistant", ExecutiveAssistantAgent(llm=self.llm))
        self.manager.register_agent("custom", CustomAgent(llm=self.llm))


state = AppState()
app = FastAPI(title="AI Work OS", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
def health():
    return {"status": "ok", "configured": state.llm.is_configured()}


@app.get("/api/agents")
def agents():
    registry = state.manager.agent_registry
    return {"agents": [
        {"type": k, "name": v.name, "capabilities": v.capabilities}
        for k, v in registry.items()
    ]}


@app.post("/api/chat")
def chat(req: ChatRequest):
    try:
        response = state.llm.chat(
            [{"role": "user", "content": req.message}],
            system_prompt=req.system_prompt
        )
        return {"response": response}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(500, str(e))


@app.post("/api/plan")
def plan(req: GoalRequest):
    try:
        result = state.manager.create_plan(req.goal)
        return result
    except Exception as e:
        logger.error(f"Plan error: {e}")
        raise HTTPException(500, str(e))


@app.post("/api/execute")
def execute(req: GoalRequest):
    try:
        plan = state.manager.create_plan(req.goal)
        result = state.manager.execute_plan(plan)
        return result
    except Exception as e:
        logger.error(f"Execute error: {e}")
        raise HTTPException(500, str(e))


@app.get("/api/memory")
def get_memory():
    return {"items": state.memory.get_all()}


@app.post("/api/memory")
def add_memory(req: MemoryRequest):
    state.memory.remember(
        key=req.key,
        content=req.content,
        category=req.category,
        tags=req.tags,
        source=req.source
    )
    return {"status": "ok"}


@app.delete("/api/memory/{key}")
def delete_memory(key: str):
    state.memory.forget(key)
    return {"status": "ok"}


@app.post("/api/graph/node")
def add_graph_node(req: GraphNodeRequest):
    node = WorkNode(
        node_id=req.node_id,
        node_type=req.node_type,
        name=req.name,
        properties=req.properties
    )
    state.work_graph.add_node(node)
    return {"status": "ok"}


@app.post("/api/graph/relation")
def add_graph_relation(req: GraphRelationRequest):
    state.work_graph.add_relation(
        source_id=req.source_id,
        target_id=req.target_id,
        relation_type=req.relation_type
    )
    return {"status": "ok"}


@app.post("/api/graph/query")
def query_graph(req: Message):
    try:
        result = state.work_graph.query(req.message)
        return {"result": result}
    except Exception as e:
        logger.error(f"Graph query error: {e}")
        raise HTTPException(500, str(e))


# Static files
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/app.js")
def app_js():
    return FileResponse(STATIC_DIR / "app.js")


@app.get("/sw.js")
def sw_js():
    return FileResponse(STATIC_DIR / "sw.js")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)