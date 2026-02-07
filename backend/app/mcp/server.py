"""MCP server for todo task operations.

This module creates an MCP server using the official MCP SDK (FastMCP).
It is run as a subprocess via MCPServerStdio from the OpenAI Agents SDK.
The server is completely stateless and contains no AI logic.
"""
from mcp.server.fastmcp import FastMCP

mcp_server = FastMCP("todo-mcp")
