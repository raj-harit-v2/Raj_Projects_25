# modules/historical_context.py
"""
Smart historical conversation indexing and retrieval system.
Stores conversations by topic for contextual lookup.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

HISTORICAL_STORE_PATH = Path(__file__).parent.parent / "historical_conversation_store.json"


class HistoricalContextManager:
    """Manages topic-based historical conversation storage and retrieval."""
    
    def __init__(self):
        self.store_path = HISTORICAL_STORE_PATH
        self.store = self._load_store()
    
    def _load_store(self) -> Dict:
        """Load historical store from disk."""
        default_structure = {
            "metadata": {
                "version": "1.0",
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "total_conversations": 0
            },
            "topics": {
                "mathematics": {"conversations": []},
                "documents": {"conversations": []},
                "finance": {"conversations": []},
                "technology": {"conversations": []},
                "web_research": {"conversations": []},
                "education": {"conversations": []},
                "general": {"conversations": []}
            },
            "index": {
                "by_hash": {},
                "by_date": [],
                "recent_topics": []
            }
        }
        
        if self.store_path.exists():
            try:
                with open(self.store_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Validate structure - if missing required keys, use default
                    if not isinstance(loaded, dict) or "index" not in loaded:
                        return default_structure
                    # Ensure all required keys exist
                    if "topics" not in loaded:
                        loaded["topics"] = default_structure["topics"]
                    else:
                        # Ensure all default topics exist in loaded topics
                        for default_topic in default_structure["topics"]:
                            if default_topic not in loaded["topics"]:
                                loaded["topics"][default_topic] = {"conversations": []}
                            elif "conversations" not in loaded["topics"][default_topic]:
                                loaded["topics"][default_topic]["conversations"] = []
                    if "metadata" not in loaded:
                        loaded["metadata"] = default_structure["metadata"]
                    if "index" not in loaded:
                        loaded["index"] = default_structure["index"]
                    # Ensure index has required sub-keys
                    if "by_hash" not in loaded["index"]:
                        loaded["index"]["by_hash"] = {}
                    if "by_date" not in loaded["index"]:
                        loaded["index"]["by_date"] = []
                    if "recent_topics" not in loaded["index"]:
                        loaded["index"]["recent_topics"] = []
                    return loaded
            except (json.JSONDecodeError, KeyError):
                # If file is corrupted or empty, return default
                return default_structure
        else:
            # Return empty structure
            return default_structure
    
    def _save_store(self):
        """Persist store to disk."""
        self.store["metadata"]["last_updated"] = datetime.utcnow().isoformat() + "Z"
        with open(self.store_path, 'w', encoding='utf-8') as f:
            json.dump(self.store, f, indent=2, ensure_ascii=False)
    
    def add_conversation(
        self,
        query: str,
        query_hash: str,
        topic: str,
        result: str,
        session_id: str,
        success: bool = True,
        metadata: Optional[Dict] = None
    ):
        """
        Add a completed conversation to the historical store.
        """
        if topic not in self.store["topics"]:
            topic = "general"
        
        # Ensure topic structure exists
        if topic not in self.store["topics"]:
            self.store["topics"][topic] = {"conversations": []}
        if "conversations" not in self.store["topics"][topic]:
            self.store["topics"][topic]["conversations"] = []
        
        conversation = {
            "query_hash": query_hash,
            "query": query[:200],  # Store truncated query
            "timestamp": time.time(),
            "date": datetime.utcnow().isoformat() + "Z",
            "topic": topic,
            "success": success,
            "result_summary": result[:500] if result else "No result",
            "session_id": session_id,
            "metadata": metadata or {}
        }
        
        # Add to topic
        self.store["topics"][topic]["conversations"].append(conversation)
        
        # Add to hash index
        self.store["index"]["by_hash"][query_hash] = {
            "topic": topic,
            "timestamp": conversation["timestamp"],
            "session_id": session_id
        }
        
        # Add to date index (keep last 100)
        self.store["index"]["by_date"].append({
            "query_hash": query_hash,
            "timestamp": conversation["timestamp"],
            "topic": topic
        })
        self.store["index"]["by_date"] = self.store["index"]["by_date"][-100:]
        
        # Update recent topics
        if topic not in self.store["index"]["recent_topics"]:
            self.store["index"]["recent_topics"].append(topic)
        self.store["index"]["recent_topics"] = self.store["index"]["recent_topics"][-10:]
        
        # Update count
        self.store["metadata"]["total_conversations"] = sum(
            len(self.store["topics"][t]["conversations"]) 
            for t in self.store["topics"]
        )
        
        self._save_store()
    
    def get_context_by_topic(self, topic: str, limit: int = 5) -> List[Dict]:
        """
        Retrieve recent successful conversations for a topic.
        """
        if topic not in self.store["topics"]:
            return []
        
        conversations = self.store["topics"][topic]["conversations"]
        
        # Filter successful, sort by timestamp (newest first)
        successful = [c for c in conversations if c.get("success", False)]
        successful.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        return successful[:limit]
    
    def check_duplicate(self, query_hash: str) -> Optional[Dict]:
        """
        Check if query was recently executed (cache hit).
        """
        if query_hash in self.store["index"]["by_hash"]:
            entry = self.store["index"]["by_hash"][query_hash]
            
            # If within last hour, consider it a duplicate
            time_diff = time.time() - entry.get("timestamp", 0)
            if time_diff < 3600:  # 1 hour
                topic = entry["topic"]
                # Find the actual conversation
                for conv in self.store["topics"][topic]["conversations"]:
                    if conv["query_hash"] == query_hash:
                        return conv
        
        return None
    
    def format_context_for_prompt(self, topic: str, limit: int = 3) -> str:
        """
        Format historical context for injection into LLM prompt.
        """
        contexts = self.get_context_by_topic(topic, limit)
        
        if not contexts:
            return "No relevant historical context available."
        
        formatted = []
        for i, ctx in enumerate(contexts, 1):
            formatted.append(
                f"{i}. Query: {ctx['query']}\n"
                f"   Result: {ctx['result_summary']}\n"
                f"   Date: {ctx['date'][:10]}"
            )
        
        return "\n\n".join(formatted)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics."""
        stats = {
            "total": self.store["metadata"]["total_conversations"],
            "by_topic": {}
        }
        
        for topic, data in self.store["topics"].items():
            stats["by_topic"][topic] = len(data["conversations"])
        
        return stats

