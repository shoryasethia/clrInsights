import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# Sessions root directory (sibling to clrinsights package)
SESSIONS_DIR = Path(__file__).parent.parent / "sessions"


class ConversationMessage(BaseModel):
    """Single message in conversation."""
    role: str
    content: str
    timestamp: Optional[str] = None


class ConversationHistory:
    """
    Manage conversation history for a session.
    Each session is a folder under sessions/<session_id>/ containing:
      - meta.json       → title, created_at, updated_at
      - messages.json    → list of all messages
      - traces/          → one JSON per query (trace_001.json, ...)
      - visualizations/  → saved PNGs (viz_001.png, ...)
    """
    
    def __init__(self, session_id: str, max_messages: int = 50):
        self.session_id = session_id
        self.max_messages = max_messages
        self.session_dir = SESSIONS_DIR / session_id
        self.messages: list[dict] = []
        self.title: str = "New Conversation"
        self.created_at: str = datetime.now().isoformat()
        self.updated_at: str = self.created_at
        
        # Create folder structure
        self.session_dir.mkdir(parents=True, exist_ok=True)
        (self.session_dir / "traces").mkdir(exist_ok=True)
        (self.session_dir / "visualizations").mkdir(exist_ok=True)
        
        # Load existing data if present
        self._load()
    
    def _load(self):
        """Load session from disk."""
        meta_path = self.session_dir / "meta.json"
        messages_path = self.session_dir / "messages.json"
        
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                self.title = meta.get("title", self.title)
                self.created_at = meta.get("created_at", self.created_at)
                self.updated_at = meta.get("updated_at", self.updated_at)
        
        if messages_path.exists():
            with open(messages_path, "r", encoding="utf-8") as f:
                self.messages = json.load(f)
    
    def _save_meta(self):
        """Save session metadata."""
        self.updated_at = datetime.now().isoformat()
        meta = {
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "session_id": self.session_id
        }
        with open(self.session_dir / "meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
    
    def _save_messages(self):
        """Save messages to disk."""
        with open(self.session_dir / "messages.json", "w", encoding="utf-8") as f:
            json.dump(self.messages, f, indent=2, default=str)
    
    def add_message(self, role: str, content: str, **extra) -> None:
        """Add message to history and auto-save.
        
        Args:
            role: 'user' or 'assistant'
            content: message text
            **extra: additional fields like visualizations, trace, error, sql_queries
        """
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        # Attach optional fields for assistant messages
        if extra.get("visualizations"):
            msg["visualizations"] = extra["visualizations"]
        if extra.get("trace"):
            msg["trace"] = extra["trace"]
        if extra.get("error"):
            msg["error"] = extra["error"]
        if extra.get("sql_queries"):
            msg["sql_queries"] = extra["sql_queries"]
        
        self.messages.append(msg)
        
        # Trim if exceeds max
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        
        self._save_messages()
        self._save_meta()
    
    def save_trace(self, trace: list[dict]) -> None:
        """Save execution trace for the latest query."""
        traces_dir = self.session_dir / "traces"
        existing = sorted(traces_dir.glob("trace_*.json"))
        idx = len(existing) + 1
        trace_file = traces_dir / f"trace_{idx:03d}.json"
        with open(trace_file, "w", encoding="utf-8") as f:
            json.dump(trace, f, indent=2, default=str)
    
    def save_visualizations(self, visualizations: list[str]) -> None:
        """Save base64 visualization images as PNGs."""
        import base64
        viz_dir = self.session_dir / "visualizations"
        existing = sorted(viz_dir.glob("viz_*.png"))
        start_idx = len(existing) + 1
        
        for i, img_b64 in enumerate(visualizations):
            if not img_b64:
                continue
            viz_file = viz_dir / f"viz_{start_idx + i:03d}.png"
            with open(viz_file, "wb") as f:
                f.write(base64.b64decode(img_b64))
    
    def save_response(self, result: dict) -> None:
        """Auto-save a complete response (trace + visualizations + messages)."""
        # Save trace
        trace = result.get("trace", [])
        if trace:
            self.save_trace(trace)
        
        # Save visualizations as PNGs
        vizs = result.get("visualizations", [])
        if vizs:
            self.save_visualizations(vizs)
        
        # Messages are already saved via add_message()
        self._save_meta()
    
    def set_title(self, title: str) -> None:
        """Set session title and save."""
        self.title = title
        self._save_meta()
    
    def get_messages(self) -> list[dict]:
        """Get all messages."""
        return self.messages
    
    def clear(self) -> None:
        """Clear conversation history."""
        self.messages = []
        self._save_messages()
    
    def delete(self) -> None:
        """Delete the entire session folder."""
        if self.session_dir.exists():
            shutil.rmtree(self.session_dir)
    
    def get_meta(self) -> dict:
        """Get session metadata."""
        return {
            "id": self.session_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "message_count": len(self.messages)
        }
    
    def get_context_string(self, max_chars: int = 2000) -> str:
        """Get conversation context as string."""
        context = []
        total_chars = 0
        
        for msg in reversed(self.messages):
            msg_str = f"{msg['role']}: {msg['content']}\n"
            if total_chars + len(msg_str) > max_chars:
                break
            context.insert(0, msg_str)
            total_chars += len(msg_str)
        
        return '\n'.join(context)


# In-memory cache of loaded sessions
_session_cache: dict[str, ConversationHistory] = {}


def get_or_create_session(session_id: str) -> ConversationHistory:
    """Get or create conversation session (loads from disk if exists)."""
    if session_id not in _session_cache:
        _session_cache[session_id] = ConversationHistory(session_id)
    return _session_cache[session_id]


def list_all_sessions() -> list[dict]:
    """List all saved sessions from disk."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    sessions = []
    for session_dir in sorted(SESSIONS_DIR.iterdir(), reverse=True):
        if session_dir.is_dir():
            meta_path = session_dir / "meta.json"
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    sessions.append({
                        "id": meta.get("session_id", session_dir.name),
                        "title": meta.get("title", "Untitled"),
                        "created_at": meta.get("created_at", ""),
                        "updated_at": meta.get("updated_at", ""),
                    })
            else:
                sessions.append({
                    "id": session_dir.name,
                    "title": "Untitled",
                    "created_at": "",
                    "updated_at": "",
                })
    # Sort by updated_at descending
    sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
    return sessions


def delete_session(session_id: str) -> bool:
    """Delete a session folder and remove from cache."""
    session = get_or_create_session(session_id)
    session.delete()
    _session_cache.pop(session_id, None)
    return True
