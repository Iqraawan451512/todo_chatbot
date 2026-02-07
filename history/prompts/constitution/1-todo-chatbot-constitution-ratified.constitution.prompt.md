---
id: 1
title: Todo Chatbot Constitution Ratified
stage: constitution
date: 2026-02-06
surface: agent
model: claude-opus-4-6
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution", "governance", "project-setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
---

## Prompt

# Phase III: Todo AI Chatbot — Specification Constitution

## 1. Purpose & Authority
This document is the **single source of truth** for Phase III of the Todo AI Chatbot project.
All planning, implementation, and evaluation **must conform exactly** to this constitution.

Any behavior, code, or design not explicitly allowed here is **out of scope**.

This project follows the **Agentic Dev Stack workflow**:

> **Write Spec → Generate Plan → Break into Tasks → Implement via Claude Code**

❌ Manual coding is **strictly prohibited**.
✅ All implementation must be generated via **Claude Code**.

---

## 2. Core Objectives

- Build an **AI-powered conversational interface** for todo management
- Enforce a **fully stateless backend**
- Use **MCP (Model Context Protocol)** tools for *all* task operations
- Persist **all state** in the database
- Resume conversations after server restarts without loss

---

## 3. Mandatory Technology Stack

| Layer | Technology |
|-----|-----------|
| Frontend | OpenAI ChatKit |
| Backend API | Python FastAPI |
| AI Framework | OpenAI Agents SDK |
| Tool Layer | Official MCP SDK |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Authentication | Better Auth |

🚫 Any deviation from this stack is **not allowed**.

---

## 4. Architectural Constitution

### 4.1 Stateless Server Rule (Non-Negotiable)

- The FastAPI server must hold **no memory**
- No in-memory sessions, caches, or globals
- Every request must be reconstructable from the database

---

### 4.2 Single Chat Endpoint

POST /api/{user_id}/chat

This is the **only** conversational endpoint.

---

### 4.3 Canonical Request Flow

1. Receive user message
2. Load conversation history from database
3. Append new user message
4. Run AI agent (OpenAI Agents SDK)
5. Agent invokes MCP tools
6. MCP tools read/write database
7. Persist assistant response
8. Return response to client

---

## 5. Database Constitution

### 5.1 Models

#### Task
| Field | Description |
|----|----|
| id | Primary key |
| user_id | Owner |
| title | Task title |
| description | Optional |
| completed | Boolean |
| created_at | Timestamp |
| updated_at | Timestamp |

#### Conversation
| Field | Description |
|----|----|
| id | Primary key |
| user_id | Owner |
| created_at | Timestamp |
| updated_at | Timestamp |

#### Message
| Field | Description |
|----|----|
| id | Primary key |
| conversation_id | Parent conversation |
| user_id | Owner |
| role | user / assistant |
| content | Text |
| created_at | Timestamp |

---

## 6. MCP Server Constitution

### 6.1 MCP Role

- Exposes **task operations as tools**
- Completely **stateless**
- Interacts **only with the database**
- Contains **no AI logic**

---

### 6.2 Required MCP Tools

#### add_task
Creates a new task

**Parameters**
- user_id (string, required)
- title (string, required)
- description (string, optional)

**Returns**
- task_id
- status
- title

---

#### list_tasks
Retrieves tasks

**Parameters**
- user_id (string, required)
- status (optional: all | pending | completed)

**Returns**
- Array of task objects

---

#### complete_task
Marks task as completed

**Parameters**
- user_id (string, required)
- task_id (integer, required)

**Returns**
- task_id
- status
- title

---

#### delete_task
Deletes a task

**Parameters**
- user_id (string, required)
- task_id (integer, required)

**Returns**
- task_id
- status
- title

---

#### update_task
Updates title or description

**Parameters**
- user_id (string, required)
- task_id (integer, required)
- title (optional)
- description (optional)

**Returns**
- task_id
- status
- title

---

## 7. AI Agent Constitution

### 7.1 Agent Authority

- Agent must **never modify tasks directly**
- All task operations **must go through MCP tools**
- Agent handles **reasoning + tool selection only**

---

### 7.2 Intent → Tool Mapping

| User Intent | Tool |
|-----------|------|
| Add / remember | add_task |
| Show / list | list_tasks |
| Done / complete | complete_task |
| Delete / remove | delete_task |
| Change / rename | update_task |

---

### 7.3 Tool Chaining Rule

If task identity is unclear:
1. Call `list_tasks`
2. Then call the mutation tool

---

## 8. Conversation Behavior Rules

- Every mutation **must be confirmed**
- Errors handled gracefully
- Invalid task IDs must not crash system
- Responses must be friendly and clear

---

## 9. Natural Language Coverage

The agent must understand:

- "Add a task to buy groceries"
- "Show me all my tasks"
- "What's pending?"
- "Mark task 3 as complete"
- "Delete the meeting task"
- "Change task 1 to 'Call mom tonight'"
- "I need to remember to pay bills"
- "What have I completed?"

---

## 10. Frontend Constitution (ChatKit)

- Must use OpenAI ChatKit
- Must call only `/api/{user_id}/chat`
- Must pass `conversation_id` when available
- Must render confirmations and errors

### Domain Allowlist (Production)

- Frontend domain must be added to OpenAI Domain Allowlist
- Environment variable required:

NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key

---

## 11. Bonus Eligibility

| Feature | Points |
|------|-------|
| Reusable Intelligence (Subagents) | +200 |
| Cloud-Native Agent Skills | +200 |
| Urdu Language Support | +100 |
| Voice Commands | +200 |

---

## 12. Evaluation Standard

Judging will consider:

- Strict adherence to this constitution
- Correct MCP tool usage
- Stateless correctness
- Process traceability (Spec → Plan → Tasks → Code)
- Restart resilience

🚫 Any violation = **non-compliant submission**

---

**End of Constitution**

## Response snapshot

Constitution v1.0.0 ratified for the Todo AI Chatbot project. Derived 7 core principles from user input: (I) Stateless Server, (II) MCP-Only Task Operations, (III) AI Agent Boundary, (IV) Database as Single Source of Truth, (V) Mandatory Technology Stack Compliance, (VI) Single Chat Endpoint, (VII) Conversation Resumability. Added two additional sections: Mandatory Technology Stack & Data Model (covering request flow, data models, MCP tool contracts, frontend rules, bonus features) and Development Workflow & Request Flow (covering Agentic Dev Stack workflow, NL coverage, conversation behavior). Governance section established with amendment procedure, semantic versioning policy, and compliance review requirements. Sync Impact Report embedded as HTML comment. All templates reviewed — plan template needs Constitution Check populated at plan time; spec and tasks templates require no changes.

## Outcome

- ✅ Impact: Project constitution established — all 7 principles codified, technology stack locked, data model defined, MCP contracts specified
- 🧪 Tests: N/A (governance document, not code)
- 📁 Files: .specify/memory/constitution.md (created/overwritten)
- 🔁 Next prompts: /sp.specify to create feature spec, /sp.plan to generate implementation plan
- 🧠 Reflection: User provided an exceptionally detailed constitution covering all layers; mapped cleanly to 7 testable principles

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review — PASS (no unresolved placeholders, all principles declarative and testable)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
