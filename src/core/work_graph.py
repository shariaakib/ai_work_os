"""
Work Graph - Understands the relationships between work items.

The Work Graph models connections between people, projects,
companies, meetings, documents, and deadlines.

Example:
    Sarah -> manages -> Project Phoenix -> belongs_to -> ABC Corp

Production-ready: AI-powered querying, persistence, and extensible node types.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class WorkNode:
    """A node in the work graph (person, project, document, etc.)."""

    def __init__(
        self,
        node_id: str,
        node_type: str,
        name: str,
        properties: Optional[Dict[str, Any]] = None,
    ):
        self.node_id = node_id
        self.node_type = node_type
        self.name = name
        self.properties = properties or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Serialize node to a dictionary."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkNode":
        """Reconstruct a WorkNode from a dictionary."""
        node = cls(
            node_id=data["node_id"],
            node_type=data["node_type"],
            name=data["name"],
            properties=data.get("properties", {}),
        )
        if "created_at" in data:
            node.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            node.updated_at = datetime.fromisoformat(data["updated_at"])
        return node

    def __repr__(self):
        return f"WorkNode({self.node_id}, {self.node_type}, {self.name})"


class WorkRelation:
    """A directed relationship between two nodes."""

    def __init__(self, source_id: str, target_id: str, relation_type: str):
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type

    def to_dict(self) -> dict:
        """Serialize relation to a dictionary."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkRelation":
        """Reconstruct a WorkRelation from a dictionary."""
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            relation_type=data["relation_type"],
        )

    def __repr__(self):
        return f"WorkRelation({self.source_id}->{self.target_id}, {self.relation_type})"



class WorkGraph:
    """A graph database that understands relationships between work items.

    Usage:
        graph = WorkGraph()
        graph.add_node(WorkNode("proj-1", "project", "Project Phoenix"))
        graph.add_relation("sarah", "proj-1", "manages")
        result = graph.query("What is blocking Project Phoenix?")
    """

    default_db_path = "data/work_graph.json"

    def __init__(self, db_path: Optional[str] = None):
        self.nodes: Dict[str, WorkNode] = {}
        self.relations: List[WorkRelation] = []
        self._llm = None
        self.db_path = Path(db_path) if db_path else Path(self.default_db_path)
        self._load()

    def set_llm(self, llm):
        """Attach an LLM client for AI-powered queries."""
        self._llm = llm

    def add_node(self, node: WorkNode):
        """Add a node to the graph and persist."""
        self.nodes[node.node_id] = node
        logger.debug("Added node: %s (%s)", node.node_id, node.node_type)
        self._save()

    def remove_node(self, node_id: str) -> bool:
        """Remove a node and all its relations."""
        if node_id not in self.nodes:
            return False
        del self.nodes[node_id]
        self.relations = [
            r for r in self.relations
            if r.source_id != node_id and r.target_id != node_id
        ]
        logger.debug("Removed node: %s", node_id)
        self._save()
        return True
    def add_relation(self, source_id: str, target_id: str, relation_type: str):
        """Add a directed relationship between two nodes and persist."""
        relation = WorkRelation(source_id, target_id, relation_type)
        self.relations.append(relation)
        logger.debug("Added relation: %s --%s--> %s", source_id, relation_type, target_id)
        self._save()

    def get_node(self, node_id: str) -> Optional[WorkNode]:
        """Retrieve a node by ID."""
        return self.nodes.get(node_id)

    def find_node_by_name(self, name: str) -> Optional[WorkNode]:
        """Find a node by its (case-insensitive) name."""
        for node in self.nodes.values():
            if node.name.lower() == name.lower():
                return node
        return None

    def get_related(self, node_id: str, relation_type: Optional[str] = None) -> List[WorkNode]:
        """Get nodes related to this node, optionally filtered by relation type."""
        result = []
        for rel in self.relations:
            if rel.source_id != node_id or (relation_type and rel.relation_type != relation_type):
                continue
            target = self.nodes.get(rel.target_id)
            if target:
                result.append(target)
        return result

    def query(self, question: str) -> str:
        """Query the graph using AI-powered natural language understanding.

        Builds a textual summary of the graph and asks the LLM to answer.
        Falls back to a structural description when no LLM is configured.
        """
        lines = []
        for nid, node in self.nodes.items():
            lines.append(f"- {node.name} (type: {node.node_type}, id: {nid})")
        for rel in self.relations:
            src = self.nodes.get(rel.source_id, WorkNode("?", "?", "?"))
            tgt = self.nodes.get(rel.target_id, WorkNode("?", "?", "?"))
            lines.append(f"  {src.name} --{rel.relation_type}--> {tgt.name}")
        graph_summary = "\n".join(lines) if lines else "The graph is empty."

        if self._llm and self._llm.is_configured():
            try:
                return self._llm.chat(
                    messages=[{"role": "user", "content": question}],
                    system_prompt=(
                        "Answer questions about this work graph.\n"
                        f"{graph_summary}\n\nBe concise."
                    ),
                )
            except Exception as e:
                logger.error("Graph AI query failed: %s", str(e))

        return f"Work graph query: '{question}'\nGraph: {graph_summary}"

    def _save(self):
        """Persist the work graph to disk."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
            "relations": [rel.to_dict() for rel in self.relations],
        }
        self.db_path.write_text(json.dumps(data, indent=2))

    def _load(self):
        """Load the work graph from disk."""
        if self.db_path.exists():
            data = json.loads(self.db_path.read_text())
            for nid, node_data in data.get("nodes", {}).items():
                self.nodes[nid] = WorkNode.from_dict(node_data)
            for rel_data in data.get("relations", []):
                self.relations.append(WorkRelation.from_dict(rel_data))

    def __repr__(self):
        return f"WorkGraph(nodes={len(self.nodes)}, relations={len(self.relations)})"