# Implementation Plan: Todo AI Chatbot

**Branch**: `001-todo-ai-chatbot` | **Date**: 2026-02-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-todo-ai-chatbot/spec.md`

## Summary

Build a stateless, AI-powered conversational chatbot for todo task
management. The system uses OpenAI Agents SDK for natural language
reasoning, MCP tools for all task CRUD operations, and Neon PostgreSQL
for persistent state. A single FastAPI endpoint
(`POST /api/{user_id}/chat`) handles all interactions. The frontend
uses OpenAI ChatKit for the chat UI.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, OpenAI Agents SDK (openai-agents
v0.8.0), MCP SDK (mcp), SQLModel, psycopg2-binary, uvicorn
**Frontend Dependencies**: Next.js, @openai/chatkit-react, better-auth
**Storage**: Neon Serverless PostgreSQL (pooled connections via
PgBouncer, `-pooler` hostname suffix, `?sslmode=require`)
**Testing**: pytest, httpx (async test client for FastAPI)
**Target Platform**: Linux server (backend), Web browser (frontend)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: < 5 seconds end-to-end response time for task
operations
**Constraints**: Zero in-memory state, all context from database,
MCP-only task operations
**Scale/Scope**: Single-user to multi-user; Neon supports up to 10K
concurrent connections via pooling

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1
design.*

- [x] **I. Stateless Server**: No in-memory state. Every request
  reconstructs context from database. No globals, caches, or
  session objects.
- [x] **II. MCP-Only Task Operations**: All 5 MCP tools defined
  (add_task, list_tasks, complete_task, delete_task, update_task).
  MCP server is stateless, no AI logic.
- [x] **III. AI Agent Boundary**: Agent handles reasoning + tool
  selection only. Never modifies DB directly. Tool chaining rule
  enforced (list before ambiguous mutation).
- [x] **IV. Database as Single Source of Truth**: All state in Neon
  PostgreSQL. Models: Task, Conversation, Message. SQLModel ORM.
  No caching outside DB.
- [x] **V. Technology Stack Compliance**: FastAPI, OpenAI Agents SDK,
  MCP SDK, SQLModel, Neon PostgreSQL, Better Auth, OpenAI ChatKit.
  No deviations.
- [x] **VI. Single Chat Endpoint**: `POST /api/{user_id}/chat` is the
  only conversational endpoint. No additional CRUD endpoints.
- [x] **VII. Conversation Resumability**: History loaded from DB on
  every request. Messages persisted. Survives server restarts.

**Result**: All 7 gates PASS. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-ai-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── chat-api.yaml    # OpenAPI contract
│   └── mcp-tools.md     # MCP tool contracts
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app bootstrap + health check
│   ├── config.py            # Settings from .env (DATABASE_URL, OPENAI_API_KEY)
│   ├── db/
│   │   ├── __init__.py
│   │   ├── engine.py        # SQLModel engine with Neon pooled connection
│   │   └── models.py        # Task, Conversation, Message SQLModel classes
│   ├── api/
│   │   ├── __init__.py
│   │   └── chat.py          # POST /api/{user_id}/chat endpoint
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── agent.py         # OpenAI Agent definition (system prompt, model)
│   │   └── runner.py        # Agent execution: load history, run, persist
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py        # MCP server setup (stdio transport)
│   │   └── tools.py         # 5 MCP tools: add/list/complete/delete/update
│   └── services/
│       ├── __init__.py
│       ├── conversations.py # get_or_create_conversation, load_history
│       └── messages.py      # save_message (user + assistant)
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures (test DB, client)
│   └── test_chat.py         # Integration tests for chat endpoint
├── requirements.txt
└── .env.example

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   └── page.tsx         # Chat page
│   ├── components/
│   │   └── ChatWidget.tsx   # ChatKit wrapper component
│   └── lib/
│       ├── auth.ts          # Better Auth client setup
│       └── api.ts           # Chat API client
├── package.json
├── next.config.js
└── .env.local
```

**Structure Decision**: Web application (Option 2) — backend/ for
Python FastAPI + frontend/ for Next.js with ChatKit. This matches
the two-language stack (Python backend, TypeScript frontend).

## Complexity Tracking

No constitution violations to justify. All complexity is within
expected bounds for the locked technology stack.

## Key Design Decisions

### 1. MCP Server Transport: Stdio (In-Process)

The MCP server runs in-process with the FastAPI backend using stdio
transport. The OpenAI Agents SDK connects to it via
`MCPServerStdio`. This avoids network overhead and simplifies
deployment while maintaining the MCP tool boundary.

### 2. Agent Session Management

Each request loads the full conversation history from the database,
constructs a message list, and passes it to the agent. The agent
runs synchronously within the request lifecycle. No session state
is held between requests.

### 3. Better Auth Integration Pattern

Better Auth runs in the Next.js frontend layer. The FastAPI backend
receives the `user_id` from the URL path, which is set by the
authenticated frontend. For MVP, the backend trusts the `user_id`
in the path. For production hardening, the backend can validate
session tokens against the shared database.

### 4. Frontend Chat Flow

The ChatKit component renders the chat UI. On message send:
1. Frontend calls `POST /api/{user_id}/chat` with the message and
   optional `conversation_id`
2. Backend processes and returns `ChatResponse`
3. Frontend stores `conversation_id` from response for subsequent
   messages
4. ChatKit renders the assistant's response

### 5. Error Handling Strategy

- MCP tools return structured error objects (not exceptions)
- The agent interprets error responses and generates friendly messages
- FastAPI catches unhandled exceptions and returns 500 with error body
- Invalid conversation_id creates a new conversation (graceful fallback)
