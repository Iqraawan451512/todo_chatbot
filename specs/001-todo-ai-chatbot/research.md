# Research: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Date**: 2026-02-06

## Technology Decisions

### 1. OpenAI Agents SDK

- **Package**: `openai-agents` v0.8.0 (PyPI)
- **Requires**: Python >= 3.9, `openai` v2.x
- **Decision**: Use OpenAI Agents SDK with built-in MCP support
- **Rationale**: Native MCP integration via `MCPServerStdio` or
  `MCPServerStreamableHttp` eliminates custom glue code. Agent
  handles reasoning and tool selection; tools are provided by MCP.
- **Alternatives considered**:
  - LangChain: Over-engineered for this use case; adds unnecessary
    abstraction layers
  - Direct OpenAI API: No built-in agent loop or MCP support

**Key patterns**:
- Define agent with `Agent(name, instructions, tools, model)`
- Run with `Runner.run(agent, messages)` passing conversation history
- Access response via `result.final_output` or `result.to_input_list()`
- MCP tools auto-discovered from connected MCP server

### 2. MCP Server (FastMCP)

- **Package**: `mcp` (official SDK, PyPI)
- **Decision**: Use official `mcp` SDK with FastMCP patterns
- **Rationale**: FastMCP was incorporated into the official MCP SDK.
  Decorator-based tool definition (`@server.tool`) matches the
  constitution's tool-per-function approach.
- **Alternatives considered**:
  - `fastmcp` standalone package: Now redundant since merged into
    official SDK
  - Custom tool protocol: Violates MCP-only constitution rule

**Key patterns**:
- Create server with `Server("todo-mcp")`
- Define tools with `@server.tool()` decorator
- Tools receive typed parameters, return structured dicts
- Each tool is stateless — receives DB session per call
- Run via stdio transport for in-process connection with agent

### 3. OpenAI ChatKit (Frontend)

- **Package**: `@openai/chatkit-react` (npm)
- **Decision**: Use ChatKit React components with custom backend
- **Rationale**: ChatKit provides drop-in chat UI. Custom backend
  mode allows routing to our FastAPI endpoint.
- **Key insight**: ChatKit uses session-based architecture. The
  backend creates sessions; frontend receives session_id and
  client_token.

**Integration approach**:
- Frontend calls `POST /api/{user_id}/chat` directly
- ChatKit renders messages and handles input
- conversation_id managed via frontend state and API responses

### 4. SQLModel + Neon PostgreSQL

- **Package**: `sqlmodel` (PyPI) + `psycopg2-binary` driver
- **Decision**: Use SQLModel with Neon pooled connections
- **Rationale**: SQLModel (SQLAlchemy + Pydantic) provides type-safe
  models that double as API schemas. Neon pooled connections support
  up to 10,000 concurrent connections via PgBouncer.
- **Connection**: Use `-pooler` hostname suffix for serverless
  compatibility. SSL required (`?sslmode=require`).
- **Alternatives considered**:
  - Raw SQLAlchemy: Loses Pydantic integration
  - Tortoise ORM: Not in the locked technology stack

### 5. Better Auth

- **Package**: `better-auth` (npm) — TypeScript only
- **Decision**: Run Better Auth as a separate auth service (Next.js
  middleware or standalone). FastAPI validates sessions/JWTs.
- **Rationale**: Better Auth is TypeScript-only; it cannot be imported
  in Python. The recommended pattern is: frontend authenticates via
  Better Auth, backend validates the session token.
- **Integration**:
  - Better Auth runs in the frontend/auth layer
  - FastAPI validates session tokens from shared DB or JWT verification
  - The `user_id` in the URL path is the authenticated user identity

### 6. Python Version

- **Decision**: Python 3.11
- **Rationale**: Stable, well-supported, good async performance.
  OpenAI Agents SDK requires >= 3.9.

### 7. Testing Framework

- **Decision**: pytest with httpx for async API testing
- **Rationale**: pytest is the standard Python testing framework.
  httpx provides async test client for FastAPI.

## Resolved Clarifications

All technical context fields are resolved. No NEEDS CLARIFICATION
items remain.
