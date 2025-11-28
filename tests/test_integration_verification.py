
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os
import asyncio

# Mock dependencies before importing agent modules
sys.modules['google.adk.code_executors.agent_engine_sandbox_code_executor'] = MagicMock()
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.client.stdio'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['tenacity'] = MagicMock()
sys.modules['flask'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['dotenv'] = MagicMock()

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.tools import GoogleCodeExecutionTool, MCPToolAdapter, ToolResult
from agent.mcp_client import MCPClientManager

class TestIntegration(unittest.TestCase):
    
    def test_google_code_execution_tool(self):
        """Test GoogleCodeExecutionTool initialization and execution."""
        # Mock the executor
        mock_executor_class = sys.modules['google.adk.code_executors.agent_engine_sandbox_code_executor'].AgentEngineSandboxCodeExecutor
        mock_executor_instance = mock_executor_class.return_value
        mock_executor_instance.execute.return_value = "Execution Result"
        
        tool = GoogleCodeExecutionTool("projects/test/locations/us-central1/reasoningEngines/123/sandboxEnvironments/456")
        
        self.assertEqual(tool.name, "google_code_execution")
        
        # Test execute
        result = tool.execute("print('hello')")
        
        self.assertTrue(result.success)
        self.assertEqual(result.output, "Execution Result")
        mock_executor_instance.execute.assert_called_with("print('hello')")

    @patch('agent.mcp_client.MCPClientManager.execute_tool', new_callable=AsyncMock)
    def test_mcp_tool_adapter(self, mock_execute):
        """Test MCPToolAdapter execution."""
        mock_manager = MCPClientManager()
        mock_execute.return_value = "MCP Result"
        
        tool = MCPToolAdapter(mock_manager, "test_tool", "A test tool")
        
        self.assertEqual(tool.name, "test_tool")
        self.assertEqual(tool.description, "A test tool")
        
        # Test execute
        result = tool.execute(arg1="value1")
        
        self.assertTrue(result.success)
        self.assertEqual(result.output, "MCP Result")
        mock_execute.assert_called_with("test_tool", {'arg1': 'value1'})

if __name__ == '__main__':
    unittest.main()
