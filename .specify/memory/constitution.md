<!--
Sync Impact Report
===================
Version change: 0.0.0 → 1.0.0 (initial ratification)
Modified principles: N/A (first version)
Added sections:
  - Core Principles (7 principles)
  - Mandatory Technology Stack & Data Model
  - Development Workflow & Request Flow
  - Governance
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md — ⚠ pending (Constitution Check
    section must be populated per these principles at plan time)
  - .specify/templates/spec-template.md — ✅ no changes required
    (template is generic; specs will reference constitution at authoring)
  - .specify/templates/tasks-template.md — ✅ no changes required
    (task phases align with MCP-first and stateless principles)
Follow-up TODOs: None
-->

# Todo AI Chatbot Constitution

## Core Principles

### I. Stateless Server (NON-NEGOTIABLE)

- The FastAPI backend MUST hold **no in-memory state**.
- No in-memory sessions, caches, conversation stores, or global
  variables are permitted.
- Every request MUST be fully reconstructable from the database alone.
- The server MUST resume operation after a restart with zero data loss.

**Rationale**: Statelessness guarantees horizontal scalability and
restart resilience — a core evaluation criterion.

### II. MCP-Only Task Operations (NON-NEGOTIABLE)

- ALL task mutations (create, read, update, delete, complete) MUST
  pass through MCP (Model Context Protocol) tools.
- The MCP server is completely stateless and interacts only with the
  database.
- The MCP server MUST contain no AI logic; it exposes pure CRUD
  operations as tools.
- Required MCP tools: `add_task`, `list_tasks`, `complete_task`,
  `delete_task`, `update_task`.

**Rationale**: MCP as the exclusive task-operation layer enforces a
clean separation between AI reasoning and data persistence.

### III. AI Agent Boundary

- The AI agent (OpenAI Agents SDK) handles **reasoning and tool
  selection only**.
- The agent MUST NEVER modify tasks directly; all mutations go through
  MCP tools.
- When task identity is ambiguous, the agent MUST call `list_tasks`
  first, then invoke the appropriate mutation tool (tool chaining rule).
- Every mutation MUST be confirmed to the user.
- Errors MUST be handled gracefully; invalid task IDs MUST NOT crash
  the system.

**Rationale**: Constraining the agent to reasoning prevents unaudited
side-effects and ensures all state changes are traceable through MCP.

### IV. Database as Single Source of Truth

- ALL persistent state MUST reside in the Neon Serverless PostgreSQL
  database.
- Required models: **Task**, **Conversation**, **Message** (schemas
  defined in the Data Model section below).
- SQLModel is the mandatory ORM.
- No data may be cached outside the database.

**Rationale**: A single authoritative data store eliminates
inconsistency and supports the stateless server guarantee.

### V. Mandatory Technology Stack Compliance

The following stack is fixed. Any deviation is a constitution violation.

| Layer | Technology |
|-------|------------|
| Frontend | OpenAI ChatKit |
| Backend API | Python FastAPI |
| AI Framework | OpenAI Agents SDK |
| Tool Layer | Official MCP SDK |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Authentication | Better Auth |

**Rationale**: A locked stack ensures consistency across all project
artifacts and prevents scope creep from technology experimentation.

### VI. Single Chat Endpoint

- The backend MUST expose exactly one conversational endpoint:
  `POST /api/{user_id}/chat`.
- No additional REST endpoints for task CRUD are permitted; all task
  operations flow through the chat endpoint via the AI agent and MCP.

**Rationale**: A single entry point simplifies the API surface and
forces all interactions through the AI-mediated conversation flow.

### VII. Conversation Resumability

- Conversation history MUST be loaded from the database on every
  request.
- New user messages MUST be appended before the agent runs.
- Assistant responses MUST be persisted after the agent completes.
- Conversations MUST survive server restarts without loss.

**Rationale**: Resumability is a core evaluation criterion and depends
on principles I (stateless) and IV (DB as source of truth).

## Mandatory Technology Stack & Data Model

### Canonical Request Flow

1. Receive user message at `POST /api/{user_id}/chat`
2. Load conversation history from database
3. Append new user message to database
4. Run AI agent (OpenAI Agents SDK)
5. Agent invokes MCP tools as needed
6. MCP tools read/write database
7. Persist assistant response to database
8. Return response to client

### Data Models

**Task**

| Field | Type | Description |
|-------|------|-------------|
| id | PK | Primary key |
| user_id | string | Owner |
| title | string | Task title |
| description | string (optional) | Details |
| completed | boolean | Completion flag |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Last modification |

**Conversation**

| Field | Type | Description |
|-------|------|-------------|
| id | PK | Primary key |
| user_id | string | Owner |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Last modification |

**Message**

| Field | Type | Description |
|-------|------|-------------|
| id | PK | Primary key |
| conversation_id | FK | Parent conversation |
| user_id | string | Owner |
| role | enum | user / assistant |
| content | text | Message body |
| created_at | timestamp | Creation time |

### MCP Tool Contracts

| Tool | Required Params | Optional Params | Returns |
|------|-----------------|-----------------|---------|
| add_task | user_id, title | description | task_id, status, title |
| list_tasks | user_id | status (all/pending/completed) | Array of task objects |
| complete_task | user_id, task_id | — | task_id, status, title |
| delete_task | user_id, task_id | — | task_id, status, title |
| update_task | user_id, task_id | title, description | task_id, status, title |

### Frontend Rules (OpenAI ChatKit)

- MUST call only `/api/{user_id}/chat`
- MUST pass `conversation_id` when available
- MUST render confirmations and errors
- Production: frontend domain MUST be on OpenAI Domain Allowlist
  (`NEXT_PUBLIC_OPENAI_DOMAIN_KEY` env var required)

### Bonus Features (Optional)

| Feature | Points |
|---------|--------|
| Reusable Intelligence (Subagents) | +200 |
| Cloud-Native Agent Skills | +200 |
| Urdu Language Support | +100 |
| Voice Commands | +200 |

## Development Workflow & Request Flow

### Agentic Dev Stack Workflow

All implementation MUST follow this sequence:

> **Write Spec -> Generate Plan -> Break into Tasks -> Implement via
> Claude Code**

- Manual coding is prohibited; all implementation MUST be generated
  via Claude Code.
- Process traceability (Spec -> Plan -> Tasks -> Code) is an
  evaluation criterion.

### Natural Language Coverage

The AI agent MUST correctly handle at minimum:

- "Add a task to buy groceries"
- "Show me all my tasks"
- "What's pending?"
- "Mark task 3 as complete"
- "Delete the meeting task"
- "Change task 1 to 'Call mom tonight'"
- "I need to remember to pay bills"
- "What have I completed?"

### Conversation Behavior

- Every mutation MUST be confirmed in the response.
- Errors MUST be handled gracefully with friendly messages.
- Invalid task IDs MUST NOT crash the system.
- Responses MUST be friendly and clear.

## Governance

- This constitution is the **single source of truth** for the Todo AI
  Chatbot project (Phase III). All planning, implementation, and
  evaluation MUST conform exactly to this document.
- Any behavior, code, or design not explicitly allowed here is out of
  scope.
- **Amendment procedure**: Propose change -> Document rationale ->
  Update constitution version -> Propagate to dependent artifacts
  (plan, spec, tasks templates).
- **Versioning policy**: Semantic versioning (MAJOR.MINOR.PATCH).
  MAJOR = principle removal/redefinition; MINOR = new principle or
  material expansion; PATCH = clarification or wording fix.
- **Compliance review**: All PRs and code reviews MUST verify
  adherence to this constitution. Any violation renders the
  submission non-compliant.

**Version**: 1.0.0 | **Ratified**: 2026-02-06 | **Last Amended**: 2026-02-06
