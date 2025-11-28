"""
Multi-Agent Orchestrator - Coordinates multiple agents in sequential/parallel workflows.
Demonstrates: Multi-agent system, Sequential agents, Loop agents
"""
import json
import time
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

from .code_reviewer import CodeReviewAgent
from .debugger import DebugAgent
from .session_manager import SessionManager
from .observability import AgentTracer, MetricsCollector


class AgentType(Enum):
    """Types of agents in the system."""
    REVIEWER = "reviewer"
    DEBUGGER = "debugger"
    FIXER = "fixer"


class WorkflowType(Enum):
    """Types of workflows."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    LOOP = "loop"


@dataclass
class AgentTask:
    """Represents a task for an agent."""
    task_id: str
    agent_type: AgentType
    input_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class WorkflowState:
    """Tracks the state of a workflow execution."""
    workflow_id: str
    workflow_type: WorkflowType
    tasks: List[AgentTask] = field(default_factory=list)
    current_task_index: int = 0
    is_complete: bool = False
    results: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class MultiAgentOrchestrator:
    """
    Orchestrates multiple agents in various workflows.
    
    Implements:
    - Sequential agent execution
    - Parallel agent execution
    - Loop-based iterative refinement
    - Session management
    - Observability (tracing & metrics)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        session_manager: Optional[SessionManager] = None,
        enable_tracing: bool = True,
        enable_metrics: bool = True,
    ):
        """
        Initialize the orchestrator.
        
        Args:
            api_key: OpenAI API key
            session_manager: Session manager for state persistence
            enable_tracing: Enable distributed tracing
            enable_metrics: Enable metrics collection
        """
        # Initialize agents
        self.reviewer_agent = CodeReviewAgent(api_key=api_key)
        self.debugger_agent = DebugAgent(api_key=api_key)
        
        # Session management
        self.session_manager = session_manager or SessionManager()
        
        # Observability
        self.tracer = AgentTracer() if enable_tracing else None
        self.metrics = MetricsCollector() if enable_metrics else None
        
        # Workflow state tracking
        self.active_workflows: Dict[str, WorkflowState] = {}
        
        # Initialize MCP Client
        from .mcp_client import MCPClientManager
        self.mcp_manager = MCPClientManager()
        
        # Initialize Tool Registry
        from .tools import ToolRegistry, GoogleCodeExecutionTool, MCPToolAdapter
        self.tool_registry = ToolRegistry()
        
        # Register Google Code Execution Tool if configured
        import config
        if config.GOOGLE_SANDBOX_RESOURCE_NAME:
            self.tool_registry.register_tool(
                GoogleCodeExecutionTool(config.GOOGLE_SANDBOX_RESOURCE_NAME)
            )
            
        # Connect to MCP servers and register tools (async)
        # Note: In a real async app, we'd await this. For now, we'll run it in a loop or assume pre-connection.
        # self._initialize_mcp()
    
    def create_workflow(
        self,
        workflow_type: WorkflowType,
        tasks: List[AgentTask],
        workflow_id: Optional[str] = None,
    ) -> str:
        """
        Create a new workflow.
        
        Args:
            workflow_type: Type of workflow to create
            tasks: List of tasks to execute
            workflow_id: Optional workflow ID
            
        Returns:
            Workflow ID
        """
        if workflow_id is None:
            workflow_id = f"wf_{int(time.time() * 1000)}"
        
        workflow = WorkflowState(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            tasks=tasks,
        )
        
        self.active_workflows[workflow_id] = workflow
        
        # Store in session
        self.session_manager.save_workflow_state(workflow_id, workflow)
        
        if self.tracer:
            self.tracer.log_event("workflow_created", {
                "workflow_id": workflow_id,
                "workflow_type": workflow_type.value,
                "num_tasks": len(tasks),
            })
        
        return workflow_id
    
    def execute_sequential_workflow(
        self,
        code: str,
        language: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a sequential workflow: Review → Debug → Fix.
        
        This demonstrates sequential agent coordination where each agent's
        output feeds into the next agent.
        
        Args:
            code: Source code to process
            language: Programming language
            session_id: Session ID for state management
            
        Returns:
            Dict with complete workflow results
        """
        workflow_id = f"seq_{int(time.time() * 1000)}"
        
        if self.tracer:
            span_id = self.tracer.start_span("sequential_workflow", {
                "workflow_id": workflow_id,
                "code_length": len(code),
            })
        
        start_time = time.time()
        results = {
            "workflow_id": workflow_id,
            "workflow_type": "sequential",
            "steps": [],
        }
        
        try:
            # Step 1: Code Review
            if self.tracer:
                self.tracer.start_span("code_review", {"parent": workflow_id})
            
            review_result = self.reviewer_agent.review_code(code, language)
            results["steps"].append({
                "step": 1,
                "agent": "CodeReviewer",
                "result": review_result,
            })
            
            if self.metrics:
                self.metrics.increment("code_reviews_completed")
            
            # Step 2: Debug if issues found
            issues = review_result.get("review", {}).get("issues", [])
            critical_issues = [i for i in issues if i.get("severity") in ["critical", "high"]]
            
            if critical_issues:
                if self.tracer:
                    self.tracer.start_span("debug_issues", {
                        "parent": workflow_id,
                        "num_issues": len(critical_issues),
                    })
                
                # Debug the most critical issue
                first_issue = critical_issues[0]
                debug_result = self.debugger_agent.debug_code(
                    code=code,
                    error_message=first_issue.get("description"),
                    language=language,
                )
                
                results["steps"].append({
                    "step": 2,
                    "agent": "Debugger",
                    "result": debug_result,
                })
                
                if self.metrics:
                    self.metrics.increment("debug_sessions_completed")
                
                # Step 3: Apply fix if available
                if debug_result.get("success"):
                    fixed_code = debug_result.get("debug", {}).get("fixed_code")
                    if fixed_code:
                        results["steps"].append({
                            "step": 3,
                            "agent": "AutoFixer",
                            "result": {
                                "success": True,
                                "fixed_code": fixed_code,
                                "original_code": code,
                            },
                        })
                        
                        if self.metrics:
                            self.metrics.increment("auto_fixes_applied")
            
            # Calculate execution time
            execution_time = time.time() - start_time
            results["execution_time_seconds"] = execution_time
            results["success"] = True
            
            if self.metrics:
                self.metrics.record_timing("sequential_workflow_duration", execution_time)
            
            # Save to session
            if session_id:
                self.session_manager.save_interaction(session_id, {
                    "type": "sequential_workflow",
                    "results": results,
                    "timestamp": datetime.now().isoformat(),
                })
        
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
            
            if self.metrics:
                self.metrics.increment("workflow_errors")
        
        finally:
            if self.tracer and span_id:
                self.tracer.end_span(span_id)
        
        return results
    
    def execute_loop_workflow(
        self,
        code: str,
        max_iterations: int = 3,
        quality_threshold: float = 0.8,
        language: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a loop-based iterative refinement workflow.
        
        This demonstrates loop agents that iteratively improve code quality
        until a threshold is met or max iterations reached.
        
        Args:
            code: Source code to refine
            max_iterations: Maximum refinement iterations
            quality_threshold: Quality score threshold (0-1)
            language: Programming language
            session_id: Session ID for state management
            
        Returns:
            Dict with refinement results
        """
        workflow_id = f"loop_{int(time.time() * 1000)}"
        
        if self.tracer:
            span_id = self.tracer.start_span("loop_workflow", {
                "workflow_id": workflow_id,
                "max_iterations": max_iterations,
            })
        
        current_code = code
        iterations = []
        
        for iteration in range(max_iterations):
            if self.tracer:
                self.tracer.log_event("iteration_start", {
                    "workflow_id": workflow_id,
                    "iteration": iteration + 1,
                })
            
            # Review current code
            review_result = self.reviewer_agent.review_code(current_code, language)
            
            # Calculate quality score
            issues = review_result.get("review", {}).get("issues", [])
            quality_score = self._calculate_quality_score(issues, len(current_code))
            
            iteration_data = {
                "iteration": iteration + 1,
                "quality_score": quality_score,
                "num_issues": len(issues),
                "review": review_result,
            }
            
            # Check if quality threshold met
            if quality_score >= quality_threshold:
                iteration_data["status"] = "threshold_met"
                iterations.append(iteration_data)
                break
            
            # Try to fix issues
            if issues:
                high_priority_issues = [i for i in issues if i.get("severity") in ["critical", "high"]]
                
                if high_priority_issues:
                    # Debug and fix
                    debug_result = self.debugger_agent.debug_code(
                        code=current_code,
                        error_message=high_priority_issues[0].get("description"),
                        language=language,
                    )
                    
                    if debug_result.get("success"):
                        fixed_code = debug_result.get("debug", {}).get("fixed_code")
                        if fixed_code and fixed_code != current_code:
                            current_code = fixed_code
                            iteration_data["fixed_code"] = fixed_code
                            iteration_data["status"] = "improved"
                        else:
                            iteration_data["status"] = "no_improvement"
                            iterations.append(iteration_data)
                            break
            
            iterations.append(iteration_data)
            
            if self.metrics:
                self.metrics.increment("loop_iterations_completed")
        
        result = {
            "workflow_id": workflow_id,
            "workflow_type": "loop",
            "success": True,
            "iterations": iterations,
            "final_code": current_code,
            "initial_quality": iterations[0]["quality_score"] if iterations else 0,
            "final_quality": iterations[-1]["quality_score"] if iterations else 0,
            "num_iterations": len(iterations),
        }
        
        # Save to session
        if session_id:
            self.session_manager.save_interaction(session_id, {
                "type": "loop_workflow",
                "results": result,
                "timestamp": datetime.now().isoformat(),
            })
        
        if self.tracer and span_id:
            self.tracer.end_span(span_id)
        
        if self.metrics:
            self.metrics.record_value("loop_workflow_iterations", len(iterations))
        
        return result
    
    def _calculate_quality_score(self, issues: List[Dict], code_length: int) -> float:
        """
        Calculate a quality score based on issues found.
        
        Args:
            issues: List of issues
            code_length: Length of code in characters
            
        Returns:
            Quality score between 0 and 1
        """
        if not issues:
            return 1.0
        
        # Weight issues by severity
        severity_weights = {
            "critical": 10,
            "high": 5,
            "medium": 2,
            "low": 1,
            "info": 0.5,
        }
        
        total_weight = sum(
            severity_weights.get(issue.get("severity", "info"), 1)
            for issue in issues
        )
        
        # Normalize by code length (issues per 100 lines)
        normalized_weight = total_weight / (code_length / 100) if code_length > 0 else total_weight
        
        # Convert to 0-1 score (higher is better)
        score = max(0, 1 - (normalized_weight / 20))
        
        return round(score, 3)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        if not self.metrics:
            return {"metrics_enabled": False}
        
        return self.metrics.get_summary()
    
    def get_trace_log(self) -> List[Dict[str, Any]]:
        """Get trace log for observability."""
        if not self.tracer:
            return []
        
        return self.tracer.get_trace_log()
    
    def export_session(self, session_id: str, filepath: str) -> None:
        """Export session data to file."""
        session_data = self.session_manager.get_session(session_id)
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)

