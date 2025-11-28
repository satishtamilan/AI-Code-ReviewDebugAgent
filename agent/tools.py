"""
Custom Tools for the agent system.
Demonstrates: Custom tools, Built-in tools integration
"""
import subprocess
import re
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod

try:
    from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor
except ImportError:
    AgentEngineSandboxCodeExecutor = None

import config
from .mcp_client import MCPClientManager


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    output: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


class BaseTool(ABC):
    """Base class for all tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool."""
        pass


class PylintTool(BaseTool):
    """
    Tool for running pylint static analysis.
    """
    
    @property
    def name(self) -> str:
        return "pylint"
    
    @property
    def description(self) -> str:
        return "Run pylint static analysis on Python code"
    
    def execute(self, code: str, **kwargs) -> ToolResult:
        """
        Run pylint on code.
        
        Args:
            code: Python code to analyze
            
        Returns:
            ToolResult with pylint output
        """
        try:
            # Write code to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            # Run pylint
            result = subprocess.run(
                ['pylint', temp_path, '--output-format=json'],
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            # Clean up
            import os
            os.unlink(temp_path)
            
            # Parse output
            import json
            try:
                issues = json.loads(result.stdout) if result.stdout else []
            except json.JSONDecodeError:
                issues = []
            
            return ToolResult(
                success=True,
                output=issues,
                metadata={'raw_output': result.stdout}
            )
        
        except FileNotFoundError:
            return ToolResult(
                success=False,
                output=[],
                error="pylint not installed. Install with: pip install pylint"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=[],
                error=str(e)
            )


class SyntaxCheckerTool(BaseTool):
    """
    Tool for checking code syntax.
    """
    
    @property
    def name(self) -> str:
        return "syntax_checker"
    
    @property
    def description(self) -> str:
        return "Check code syntax validity"
    
    def execute(self, code: str, language: str = "python", **kwargs) -> ToolResult:
        """
        Check code syntax.
        
        Args:
            code: Code to check
            language: Programming language
            
        Returns:
            ToolResult with syntax check result
        """
        if language == "python":
            return self._check_python_syntax(code)
        elif language == "javascript":
            return self._check_javascript_syntax(code)
        else:
            return ToolResult(
                success=False,
                output=None,
                error=f"Syntax checking not supported for {language}"
            )
    
    def _check_python_syntax(self, code: str) -> ToolResult:
        """Check Python syntax."""
        try:
            import ast
            ast.parse(code)
            return ToolResult(
                success=True,
                output={"valid": True, "message": "Syntax is valid"}
            )
        except SyntaxError as e:
            return ToolResult(
                success=True,
                output={
                    "valid": False,
                    "line": e.lineno,
                    "offset": e.offset,
                    "message": e.msg,
                    "text": e.text,
                }
            )
    
    def _check_javascript_syntax(self, code: str) -> ToolResult:
        """Check JavaScript syntax (basic)."""
        # Basic JavaScript syntax patterns
        errors = []
        
        # Check for common syntax errors
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Unclosed brackets
            open_count = line.count('{') + line.count('[') + line.count('(')
            close_count = line.count('}') + line.count(']') + line.count(')')
            
            if open_count != close_count:
                errors.append({
                    "line": i,
                    "message": "Possibly unclosed brackets",
                })
        
        if errors:
            return ToolResult(
                success=True,
                output={"valid": False, "errors": errors}
            )
        
        return ToolResult(
            success=True,
            output={"valid": True, "message": "No obvious syntax errors"}
        )


class ComplexityAnalyzerTool(BaseTool):
    """
    Tool for analyzing code complexity.
    """
    
    @property
    def name(self) -> str:
        return "complexity_analyzer"
    
    @property
    def description(self) -> str:
        return "Analyze code complexity metrics"
    
    def execute(self, code: str, **kwargs) -> ToolResult:
        """
        Analyze code complexity.
        
        Args:
            code: Code to analyze
            
        Returns:
            ToolResult with complexity metrics
        """
        try:
            metrics = self._calculate_metrics(code)
            
            return ToolResult(
                success=True,
                output=metrics
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output={},
                error=str(e)
            )
    
    def _calculate_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate various complexity metrics."""
        lines = code.split('\n')
        
        # Basic metrics
        total_lines = len(lines)
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        blank_lines = len([l for l in lines if not l.strip()])
        comment_lines = len([l for l in lines if l.strip().startswith('#')])
        
        # Cyclomatic complexity (simplified)
        decision_points = 0
        for line in lines:
            decision_points += len(re.findall(r'\b(if|elif|else|for|while|and|or|case|catch)\b', line))
        
        # Nesting depth
        max_nesting = 0
        current_nesting = 0
        for line in lines:
            indent = len(line) - len(line.lstrip())
            current_nesting = indent // 4  # Assuming 4-space indents
            max_nesting = max(max_nesting, current_nesting)
        
        # Function count
        function_count = len(re.findall(r'\bdef\s+\w+\s*\(|\bfunction\s+\w+\s*\(', code))
        
        return {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "blank_lines": blank_lines,
            "comment_lines": comment_lines,
            "comment_ratio": comment_lines / code_lines if code_lines > 0 else 0,
            "cyclomatic_complexity": decision_points + 1,
            "max_nesting_depth": max_nesting,
            "function_count": function_count,
            "avg_function_length": code_lines / function_count if function_count > 0 else 0,
        }


class SecurityScannerTool(BaseTool):
    """
    Tool for scanning code for security issues.
    """
    
    @property
    def name(self) -> str:
        return "security_scanner"
    
    @property
    def description(self) -> str:
        return "Scan code for common security vulnerabilities"
    
    def execute(self, code: str, language: str = "python", **kwargs) -> ToolResult:
        """
        Scan code for security issues.
        
        Args:
            code: Code to scan
            language: Programming language
            
        Returns:
            ToolResult with security findings
        """
        findings = []
        
        if language == "python":
            findings = self._scan_python(code)
        elif language == "javascript":
            findings = self._scan_javascript(code)
        
        return ToolResult(
            success=True,
            output={
                "vulnerabilities_found": len(findings),
                "findings": findings,
            }
        )
    
    def _scan_python(self, code: str) -> List[Dict[str, Any]]:
        """Scan Python code for security issues."""
        findings = []
        lines = code.split('\n')
        
        patterns = [
            (r'\beval\s*\(', "Use of eval() is dangerous", "high"),
            (r'\bexec\s*\(', "Use of exec() is dangerous", "high"),
            (r'__import__\s*\(', "Dynamic imports can be risky", "medium"),
            (r'pickle\.loads?\s*\(', "Pickle deserialization can be unsafe", "high"),
            (r'os\.system\s*\(', "Use subprocess instead of os.system", "medium"),
            (r'shell\s*=\s*True', "shell=True in subprocess is risky", "high"),
            (r'password\s*=\s*["\']', "Hardcoded password detected", "critical"),
            (r'api[_-]?key\s*=\s*["\']', "Hardcoded API key detected", "critical"),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, message, severity in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append({
                        "line": i,
                        "severity": severity,
                        "type": "security",
                        "message": message,
                        "code": line.strip(),
                    })
        
        return findings
    
    def _scan_javascript(self, code: str) -> List[Dict[str, Any]]:
        """Scan JavaScript code for security issues."""
        findings = []
        lines = code.split('\n')
        
        patterns = [
            (r'\beval\s*\(', "Use of eval() is dangerous", "high"),
            (r'innerHTML\s*=', "innerHTML can lead to XSS", "medium"),
            (r'document\.write\s*\(', "document.write can be unsafe", "medium"),
            (r'dangerouslySetInnerHTML', "Be careful with dangerouslySetInnerHTML", "medium"),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, message, severity in patterns:
                if re.search(pattern, line):
                    findings.append({
                        "line": i,
                        "severity": severity,
                        "type": "security",
                        "message": message,
                        "code": line.strip(),
                    })
        
        return findings


class ToolRegistry:
    """
    Registry for managing and executing tools.
    """
    
    def __init__(self):
        """Initialize tool registry."""
        self.tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self) -> None:
        """Register default tools."""
        default_tools = [
            PylintTool(),
            SyntaxCheckerTool(),
            ComplexityAnalyzerTool(),
            SecurityScannerTool(),
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: BaseTool) -> None:
        """
        Register a tool.
        
        Args:
            tool: Tool instance
        """
        self.tools[tool.name] = tool
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Tool name
            
        Returns:
            Tool instance or None
        """
        return self.tools.get(tool_name)
    
    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Execute a tool.
        
        Args:
            tool_name: Tool name
            **kwargs: Tool arguments
            
        Returns:
            ToolResult
        """
        tool = self.get_tool(tool_name)
        
        if tool is None:
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool '{tool_name}' not found"
            )
        
        return tool.execute(**kwargs)
    
    def list_tools(self) -> List[Dict[str, str]]:
        """
        List all registered tools.
        
        Returns:
            List of tool info dicts
        """
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self.tools.values()
        ]


class GoogleCodeExecutionTool(BaseTool):
    """
    Tool for executing code in a secure Google Cloud Sandbox.
    """
    
    def __init__(self, sandbox_resource_name: str):
        self.sandbox_resource_name = sandbox_resource_name
        self.executor = None
        if AgentEngineSandboxCodeExecutor:
            self.executor = AgentEngineSandboxCodeExecutor(
                sandbox_resource_name=sandbox_resource_name
            )
    
    @property
    def name(self) -> str:
        return "google_code_execution"
    
    @property
    def description(self) -> str:
        return "Executes Python code in a secure Google Cloud Sandbox. Use this for running code safely."
    
    def execute(self, code: str, **kwargs) -> ToolResult:
        """
        Execute code in the sandbox.
        
        Args:
            code: Python code to execute
            
        Returns:
            ToolResult with execution output
        """
        if not self.executor:
            return ToolResult(
                success=False,
                output=None,
                error="Google Cloud Agent Engine SDK not installed or configured."
            )
            
        try:
            # The executor returns a result object, we need to parse it
            result = self.executor.execute(code)
            
            return ToolResult(
                success=True,
                output=str(result),
                metadata={"sandbox": self.sandbox_resource_name}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=f"Code execution failed: {str(e)}"
            )


class MCPToolAdapter(BaseTool):
    """
    Adapter to expose an MCP tool as a BaseTool.
    """
    
    def __init__(self, mcp_manager: MCPClientManager, tool_name: str, tool_description: str):
        self.mcp_manager = mcp_manager
        self._name = tool_name
        self._description = tool_description
        
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the MCP tool.
        
        Args:
            **kwargs: Arguments to pass to the tool
            
        Returns:
            ToolResult with execution output
        """
        try:
            # We need to run the async execution in a sync context for now
            # since BaseTool.execute is sync.
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.mcp_manager.execute_tool(self._name, kwargs)
            )
            loop.close()
            
            # MCP result structure handling
            output = ""
            if hasattr(result, 'content'):
                for item in result.content:
                    if hasattr(item, 'text'):
                        output += item.text + "\n"
                    else:
                        output += str(item) + "\n"
            else:
                output = str(result)
                
            return ToolResult(
                success=True,
                output=output.strip()
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=f"MCP tool execution failed: {str(e)}"
            )
