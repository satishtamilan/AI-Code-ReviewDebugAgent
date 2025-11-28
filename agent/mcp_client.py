"""
MCP Client Manager - Handles connections to Model Context Protocol servers.
"""
import asyncio
import json
import os
import sys
from typing import Dict, List, Optional, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import config

class MCPClientManager:
    """
    Manages connections to multiple MCP servers and exposes their tools.
    """
    
    def __init__(self):
        """Initialize the MCP Client Manager."""
        self.server_config = config.MCP_SERVER_CONFIG
        self.sessions: List[ClientSession] = []
        self.exit_stack = AsyncExitStack()
        self.tools: Dict[str, Any] = {}
        self.tool_to_session: Dict[str, ClientSession] = {}
        
    async def connect(self):
        """Connect to all configured MCP servers."""
        if not self.server_config:
            print("No MCP servers configured.")
            return

        print(f"Connecting to {len(self.server_config)} MCP servers...")
        
        for server_conf in self.server_config:
            command = server_conf.get("command")
            args = server_conf.get("args", [])
            env = server_conf.get("env", None)
            
            if not command:
                continue
                
            try:
                server_params = StdioServerParameters(
                    command=command,
                    args=args,
                    env=env
                )
                
                # Create connection context
                stdio_transport = await self.exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
                read, write = stdio_transport
                
                # Create session context
                session = await self.exit_stack.enter_async_context(
                    ClientSession(read, write)
                )
                
                await session.initialize()
                self.sessions.append(session)
                
                # Discover tools
                await self._discover_tools(session)
                
                print(f"Connected to MCP server: {command} {args}")
                
            except Exception as e:
                print(f"Failed to connect to MCP server {command}: {e}")
                
    async def _discover_tools(self, session: ClientSession):
        """Discover tools from a connected session."""
        try:
            result = await session.list_tools()
            for tool in result.tools:
                tool_name = tool.name
                # Avoid naming collisions by prefixing if necessary, 
                # but for now assume unique names or let last write win
                self.tools[tool_name] = tool
                self.tool_to_session[tool_name] = session
                print(f"Discovered MCP tool: {tool_name}")
        except Exception as e:
            print(f"Failed to list tools from session: {e}")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all discovered tools in a format suitable for the agent."""
        tool_list = []
        for name, tool in self.tools.items():
            tool_list.append({
                "name": name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            })
        return tool_list

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool on the appropriate MCP server."""
        session = self.tool_to_session.get(tool_name)
        if not session:
            raise ValueError(f"Tool {tool_name} not found or not connected.")
            
        try:
            result = await session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            raise RuntimeError(f"MCP tool execution failed: {e}")

    async def cleanup(self):
        """Close all connections."""
        await self.exit_stack.aclose()
