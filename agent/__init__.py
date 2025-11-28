"""
Code Review and Debug Agent package.

Implements key concepts for Kaggle Agents Intensive Capstone:
- Multi-agent system (sequential, parallel, loop agents)
- Custom tools (static analysis, security scanning)
- Sessions & Memory (state management, long-term memory)
- Observability (logging, tracing, metrics)
- Context engineering (summarization, compaction)
"""
from .code_reviewer import CodeReviewAgent
from .debugger import DebugAgent
from .multi_agent_orchestrator import MultiAgentOrchestrator
from .session_manager import SessionManager, MemoryBank
from .observability import AgentTracer, MetricsCollector
from .tools import ToolRegistry
from .context_engineering import ContextCompactor

__all__ = [
    "CodeReviewAgent",
    "DebugAgent",
    "MultiAgentOrchestrator",
    "SessionManager",
    "MemoryBank",
    "AgentTracer",
    "MetricsCollector",
    "ToolRegistry",
    "ContextCompactor",
]
__version__ = "2.0.0"


