"""Entry point for running the MCP server as a subprocess.

This script is invoked by MCPServerStdio from the OpenAI Agents SDK.
It starts the MCP server with stdio transport.
"""
import sys
import os

# Ensure the backend app package is importable
sys.path.insert(0, os.path.dirname(__file__))

from app.mcp.server import mcp_server
import app.mcp.tools  # noqa: F401 — registers tools with the server

if __name__ == "__main__":
    mcp_server.run(transport="stdio")
