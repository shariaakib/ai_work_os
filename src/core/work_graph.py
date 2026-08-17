"""
Work Graph - Understands the relationships between work items.

The Work Graph models connections between people, projects,
companies, meetings, documents, and deadlines.

Example:
    Sarah -> manages -> Project Phoenix -> belongs_to -> ABC Corp
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path


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
        self.node_type = node_type  # person, project, company, meeting, document, task
        self.name = name
        self.properties = properties or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class WorkRelation:
    """A relationship between two nodes."""

    def __init__(self, source_id: str, target_id: str, relation_type: str):
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type  # manages, belongs_to, related_to, requires, deadline

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
        }


class WorkGraph:
    """
    A graph database that understands relationships between work items.

    Usage:
        graph = WorkGraph()
        graph.add_node(WorkNode("proj-1", "project", "Project Phoenix"))
        graph.add_relation("sarah", "proj-1", "manages")
        result = graph.query("What is blocking Project Phoenix?")
    """

    # Overridable at runtime (tests set this to a temp dir).
    default_db_path = "data/work_graph.json"

    def __init__(self, db_path: Optional[str] = None):
        self.nodes: Dict[str, WorkNode] = {}
        self.relations: List[WorkRelation] = []
        # Default path is looked up at runtime so tests can override it
        # (see tests/conftest.py) instead of being frozen at class creation.
        self.db_path = Path(db_path) if db_path else Path(self.default_db_path)
        self._load()

    def add_node(self, node: WorkNode):
        """Add a node to the work graph."""
        self.nodes[node.node_id] = node
        self._save()

    def add_relation(self, source_id: str, target_id: str, relation_type: str):
        """Add a relationship between two nodes."""
        relation = WorkRelation(source_id, target_id, relation_type)
        self.relations.append(relation)
        self._save()

    def get_related(self, node_id: str, relation_type: Optional[str] = None) -> List[WorkNode]:
        """Get all nodes related to a given node."""
        related = []
        for rel in self.relations:
            if rel.source_id == node_id and (
                relation_type is None or rel.relation_type == relation_type
            ):
                target = self.nodes.get(rel.target_id)
                if target:
                    related.append(target)
        return related

    def query(self, question: str) -> str:
        """
        Query the work graph (placeholder for AI-powered query).

        In the full implementation, this would use an AI model
        to understand the question and traverse the graph.
        """
        return f"Work graph query: '{question}' — full AI query coming soon"

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
                node = WorkNode(
                    node_id=node_data["node_id"],
                    node_type=node_data["node_type"],
                    name=node_data["name"],
                    properties=node_data.get("properties", {}),
                )
                self.nodes[nid] = node
            for rel_data in data.get("relations", []):
                rel = WorkRelation(
                    source_id=rel_data["source_id"],
                    target_id=rel_data["target_id"],
                    relation_type=rel_data["relation_type"],
                )
                self.relations.append(rel)

    def __repr__(self):
        return f"WorkGraph(nodes={len(self.nodes)}, relations={len(self.relations)})"