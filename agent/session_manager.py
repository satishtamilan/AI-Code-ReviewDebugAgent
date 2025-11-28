"""
Session and Memory Management.
Demonstrates: Sessions & Memory, State management, Long-term memory
"""
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class SessionState:
    """Represents a session's state."""
    session_id: str
    created_at: datetime
    updated_at: datetime
    interactions: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """
    Manages sessions and maintains conversation state.
    
    Implements:
    - Session creation and management
    - State persistence
    - Interaction history
    - Context tracking
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize session manager.
        
        Args:
            storage_path: Path to store session data
        """
        self.sessions: Dict[str, SessionState] = {}
        self.storage_path = Path(storage_path) if storage_path else Path(".sessions")
        self.storage_path.mkdir(exist_ok=True)
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Create a new session.
        
        Args:
            session_id: Optional session ID
            
        Returns:
            Session ID
        """
        if session_id is None:
            session_id = f"session_{int(time.time() * 1000)}"
        
        session = SessionState(
            session_id=session_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        self.sessions[session_id] = session
        self._persist_session(session)
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None
        """
        if session_id in self.sessions:
            return asdict(self.sessions[session_id])
        
        # Try to load from storage
        return self._load_session(session_id)
    
    def save_interaction(
        self,
        session_id: str,
        interaction: Dict[str, Any],
    ) -> None:
        """
        Save an interaction to a session.
        
        Args:
            session_id: Session ID
            interaction: Interaction data
        """
        if session_id not in self.sessions:
            # Try to load or create
            session_data = self._load_session(session_id)
            if session_data:
                self.sessions[session_id] = SessionState(**session_data)
            else:
                self.create_session(session_id)
        
        session = self.sessions[session_id]
        session.interactions.append({
            **interaction,
            "timestamp": datetime.now().isoformat(),
        })
        session.updated_at = datetime.now()
        
        self._persist_session(session)
    
    def update_context(
        self,
        session_id: str,
        context_updates: Dict[str, Any],
    ) -> None:
        """
        Update session context.
        
        Args:
            session_id: Session ID
            context_updates: Context updates
        """
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        session = self.sessions[session_id]
        session.context.update(context_updates)
        session.updated_at = datetime.now()
        
        self._persist_session(session)
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get session context.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session context
        """
        if session_id not in self.sessions:
            session_data = self._load_session(session_id)
            if session_data:
                return session_data.get("context", {})
            return {}
        
        return self.sessions[session_id].context
    
    def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get interaction history.
        
        Args:
            session_id: Session ID
            limit: Limit number of interactions returned
            
        Returns:
            List of interactions
        """
        if session_id not in self.sessions:
            session_data = self._load_session(session_id)
            if session_data:
                interactions = session_data.get("interactions", [])
            else:
                interactions = []
        else:
            interactions = self.sessions[session_id].interactions
        
        if limit:
            return interactions[-limit:]
        return interactions
    
    def save_workflow_state(
        self,
        workflow_id: str,
        workflow_state: Any,
    ) -> None:
        """
        Save workflow state.
        
        Args:
            workflow_id: Workflow ID
            workflow_state: Workflow state object
        """
        # Create a pseudo-session for workflow
        session_id = f"workflow_{workflow_id}"
        
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        self.save_interaction(session_id, {
            "type": "workflow_state",
            "workflow_id": workflow_id,
            "state": asdict(workflow_state) if hasattr(workflow_state, '__dict__') else workflow_state,
        })
    
    def _persist_session(self, session: SessionState) -> None:
        """
        Persist session to storage.
        
        Args:
            session: Session state
        """
        filepath = self.storage_path / f"{session.session_id}.json"
        
        with open(filepath, 'w') as f:
            json.dump(asdict(session), f, indent=2, default=str)
    
    def _load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session from storage.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None
        """
        filepath = self.storage_path / f"{session_id}.json"
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                # Convert string dates back to datetime
                data['created_at'] = datetime.fromisoformat(data['created_at'])
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                return data
        except Exception:
            return None
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear a session.
        
        Args:
            session_id: Session ID
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        filepath = self.storage_path / f"{session_id}.json"
        if filepath.exists():
            filepath.unlink()


class MemoryBank:
    """
    Long-term memory storage for agent learnings.
    
    Implements:
    - Long-term memory storage
    - Pattern recognition
    - Knowledge base
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize memory bank.
        
        Args:
            storage_path: Path to store memory data
        """
        self.storage_path = Path(storage_path) if storage_path else Path(".memory_bank")
        self.storage_path.mkdir(exist_ok=True)
        
        self.memories: Dict[str, List[Dict[str, Any]]] = {
            "code_patterns": [],
            "common_bugs": [],
            "fix_strategies": [],
            "review_insights": [],
        }
        
        self._load_memories()
    
    def store_memory(
        self,
        category: str,
        memory: Dict[str, Any],
    ) -> None:
        """
        Store a memory.
        
        Args:
            category: Memory category
            memory: Memory data
        """
        if category not in self.memories:
            self.memories[category] = []
        
        memory["stored_at"] = datetime.now().isoformat()
        self.memories[category].append(memory)
        
        # Keep only last 1000 memories per category
        if len(self.memories[category]) > 1000:
            self.memories[category] = self.memories[category][-1000:]
        
        self._persist_memories()
    
    def retrieve_memories(
        self,
        category: str,
        limit: Optional[int] = None,
        filter_fn: Optional[callable] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories.
        
        Args:
            category: Memory category
            limit: Limit number of memories
            filter_fn: Optional filter function
            
        Returns:
            List of memories
        """
        memories = self.memories.get(category, [])
        
        if filter_fn:
            memories = [m for m in memories if filter_fn(m)]
        
        if limit:
            memories = memories[-limit:]
        
        return memories
    
    def get_common_patterns(self, category: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get most common patterns from memory.
        
        Args:
            category: Memory category
            top_n: Number of top patterns
            
        Returns:
            List of common patterns
        """
        memories = self.memories.get(category, [])
        
        # Count patterns
        pattern_counts: Dict[str, int] = {}
        pattern_data: Dict[str, Dict] = {}
        
        for memory in memories:
            pattern = memory.get("pattern", memory.get("type", "unknown"))
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            pattern_data[pattern] = memory
        
        # Sort by frequency
        sorted_patterns = sorted(
            pattern_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        return [
            {
                "pattern": pattern,
                "count": count,
                "data": pattern_data.get(pattern, {}),
            }
            for pattern, count in sorted_patterns
        ]
    
    def _persist_memories(self) -> None:
        """Persist memories to storage."""
        filepath = self.storage_path / "memories.json"
        
        with open(filepath, 'w') as f:
            json.dump(self.memories, f, indent=2, default=str)
    
    def _load_memories(self) -> None:
        """Load memories from storage."""
        filepath = self.storage_path / "memories.json"
        
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    self.memories = json.load(f)
            except Exception:
                pass

