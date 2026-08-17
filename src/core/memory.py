"""
Persistent Work Memory - Learns and stores user context and preferences.

The AI should gradually understand the user's workplace:
- "I prefer short client emails"
- "Project Phoenix is high priority"
- "Never send external emails without my approval"
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path


class MemoryItem:
    """A single piece of stored memory."""

    def __init__(
        self,
        key: str,
        content: str,
        category: str = "preference",
        tags: Optional[List[str]] = None,
        source: str = "user",
    ):
        self.key = key
        self.content = content
        self.category = category  # preference, fact, rule, context
        self.tags = tags or []
        self.source = source
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "content": self.content,
            "category": self.category,
            "tags": self.tags,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class WorkMemory:
    """
    Persistent memory that learns user preferences and workplace context.

    The user controls what the AI remembers.
    Memory belongs to the user, not secretly to the AI.

    Usage:
        memory = WorkMemory()
        memory.remember("email_style", "I prefer short client emails")
        style = memory.recall("email_style")
        all_prefs = memory.get_by_category("preference")
    """

    def __init__(self, db_path: str = "data/memory.json", max_items: int = 1000):
        self.items: Dict[str, MemoryItem] = {}
        self.max_items = max_items
        self.db_path = Path(db_path)
        self._load()

    def remember(
        self,
        key: str,
        content: str,
        category: str = "preference",
        tags: Optional[List[str]] = None,
        source: str = "user",
    ):
        """Store a memory item."""
        if key in self.items:
            existing = self.items[key]
            existing.content = content
            existing.category = category
            existing.tags = tags or []
            existing.updated_at = datetime.now()
        else:
            if len(self.items) >= self.max_items:
                # Remove oldest item
                oldest_key = min(self.items.keys(), key=lambda k: self.items[k].created_at)
                del self.items[oldest_key]
            self.items[key] = MemoryItem(key, content, category, tags, source)
        self._save()

    def recall(self, key: str) -> Optional[str]:
        """Retrieve a memory by key."""
        item = self.items.get(key)
        return item.content if item else None

    def forget(self, key: str):
        """Delete a memory."""
        if key in self.items:
            del self.items[key]
            self._save()

    def get_by_category(self, category: str) -> List[MemoryItem]:
        """Get all memories in a category."""
        return [item for item in self.items.values() if item.category == category]

    def search(self, query: str) -> List[MemoryItem]:
        """Search memories by content (simple keyword match)."""
        query_lower = query.lower()
        return [
            item
            for item in self.items.values()
            if query_lower in item.content.lower()
        ]

    def clear(self):
        """Clear all memories."""
        self.items.clear()
        self._save()

    def get_all(self) -> List[MemoryItem]:
        """Get all stored memories."""
        return list(self.items.values())

    def _save(self):
        """Persist memory to disk."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        data = {key: item.to_dict() for key, item in self.items.items()}
        self.db_path.write_text(json.dumps(data, indent=2))

    def _load(self):
        """Load memory from disk."""
        if self.db_path.exists():
            data = json.loads(self.db_path.read_text())
            for key, item_data in data.items():
                item = MemoryItem(
                    key=item_data["key"],
                    content=item_data["content"],
                    category=item_data.get("category", "preference"),
                    tags=item_data.get("tags", []),
                    source=item_data.get("source", "user"),
                )
                self.items[key] = item

    def __repr__(self):
        return f"WorkMemory(items={len(self.items)})"