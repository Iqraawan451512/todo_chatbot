# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/001-todo-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in the feature specification. Tests are included only in the final verification phase.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/src/`
- Backend uses Python (FastAPI), Frontend uses TypeScript (Next.js)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependency configuration, folder structure

- [x] T001 Create backend project structure with all directories per plan in backend/app/ (api/, agent/, db/, mcp/, services/ with __init__.py files)
- [x] T002 Create backend/requirements.txt with dependencies: fastapi, uvicorn, sqlmodel, psycopg2-binary, openai-agents, mcp, python-dotenv
- [x] T003 [P] Create backend/.env.example with DATABASE_URL, OPENAI_API_KEY placeholders
- [x] T004 [P] Create frontend project scaffolding: initialize Next.js app in frontend/ with package.json

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Implement environment configuration in backend/app/config.py — load DATABASE_URL and OPENAI_API_KEY from .env using python-dotenv, expose as Settings class
- [x] T006 Implement SQLModel engine with Neon pooled connection in backend/app/db/engine.py — create engine from DATABASE_URL, create get_session dependency yielding Session
- [x] T007 [P] Implement Task model in backend/app/db/models.py — fields: id (PK), user_id (str, indexed), title (str), description (optional str), completed (bool, default=False), created_at, updated_at per data-model.md
- [x] T008 [P] Implement Conversation model in backend/app/db/models.py — fields: id (PK), user_id (str, indexed), created_at, updated_at per data-model.md
- [x] T009 [P] Implement Message model in backend/app/db/models.py — fields: id (PK), conversation_id (FK to Conversation), user_id (str), role (str: user/assistant), content (text), created_at per data-model.md
- [x] T010 Create database table initialization in backend/app/db/engine.py — add create_tables() function using SQLModel.metadata.create_all(engine)
- [x] T011 Implement FastAPI app bootstrap in backend/app/main.py — create app, add startup event to call create_tables(), add /health endpoint
- [x] T012 Implement MCP server initialization in backend/app/mcp/server.py — create MCP Server instance with stdio transport, register tool decorator pattern per research.md
- [x] T013 Implement conversation service in backend/app/services/conversations.py — get_or_create_conversation(user_id, conversation_id, session) and load_history(conversation_id, session) returning list of messages
- [x] T014 Implement message persistence service in backend/app/services/messages.py — save_message(conversation_id, user_id, role, content, session) storing Message to DB

**Checkpoint**: Foundation ready — database, models, MCP server scaffold, and services operational. User story implementation can now begin.

---

## Phase 3: User Story 1 - Add and List Tasks via Chat (Priority: P1) MVP

**Goal**: Users can add tasks and list tasks through natural language chat messages. This proves the full end-to-end pipeline: chat endpoint -> AI agent -> MCP tools -> database -> response.

**Independent Test**: Send "Add a task to buy groceries" and verify task created. Send "Show me all my tasks" and verify list returned.

### Implementation for User Story 1

- [x] T015 [US1] Implement add_task MCP tool in backend/app/mcp/tools.py — params: user_id (str, required), title (str, required), description (str, optional). Creates Task in DB, returns {task_id, status: "created", title}
- [x] T016 [US1] Implement list_tasks MCP tool in backend/app/mcp/tools.py — params: user_id (str, required), status (str, optional: all/pending/completed, default: all). Queries Task table with filters, returns array of task objects
- [x] T017 [US1] Implement agent definition in backend/app/agent/agent.py — create Agent with name="Todo Assistant", system prompt enforcing MCP-only operations, confirmation responses, tool chaining rule, English support. Connect to MCP server tools
- [x] T018 [US1] Implement agent runner in backend/app/agent/runner.py — run_agent(agent, conversation_history, user_message) function that passes messages to agent, collects response text and tool calls, returns structured result
- [x] T019 [US1] Implement chat endpoint in backend/app/api/chat.py — POST /api/{user_id}/chat accepting ChatRequest(message, conversation_id?), orchestrating: resolve conversation, load history, persist user message, run agent, persist assistant message, return ChatResponse(conversation_id, response, tool_calls)
- [x] T020 [US1] Register chat router in backend/app/main.py — include chat.router in the FastAPI app

**Checkpoint**: At this point, User Story 1 should be fully functional. Users can add tasks and list tasks via natural language through the chat endpoint. Test by sending curl requests.

---

## Phase 4: User Story 2 - Complete, Delete, and Update Tasks (Priority: P2)

**Goal**: Users can mark tasks as done, delete tasks, and update task titles/descriptions through natural language.

**Independent Test**: Create tasks via US1, then send "Mark task 1 as complete", "Delete task 2", "Change task 3 to 'New title'" and verify each mutation.

### Implementation for User Story 2

- [x] T021 [US2] Implement complete_task MCP tool in backend/app/mcp/tools.py — params: user_id (str), task_id (int). Sets completed=True, returns {task_id, status: "completed", title}. Error if task not found or wrong user
- [x] T022 [US2] Implement delete_task MCP tool in backend/app/mcp/tools.py — params: user_id (str), task_id (int). Deletes task row, returns {task_id, status: "deleted", title}. Error if task not found or wrong user
- [x] T023 [US2] Implement update_task MCP tool in backend/app/mcp/tools.py — params: user_id (str), task_id (int), title (optional), description (optional). Updates fields, returns {task_id, status: "updated", title}. Error if not found or no fields provided
- [x] T024 [US2] Update agent system prompt in backend/app/agent/agent.py — add intent mappings for complete/delete/update, tool chaining rule (list_tasks first when task identity is ambiguous), error handling instructions

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. All 5 MCP tools (add, list, complete, delete, update) are operational.

---

## Phase 5: User Story 3 - Conversation Persistence and Resume (Priority: P3)

**Goal**: Conversations survive server restarts. Users can resume conversations with full history preserved.

**Independent Test**: Start a conversation, add tasks, stop/restart the backend, then send a new message with the same conversation_id and verify history is intact.

### Implementation for User Story 3

- [x] T025 [US3] Verify statelessness in backend/app/main.py — audit for any global variables, in-memory caches, or session objects. Remove any found. Ensure app has zero server-side state
- [x] T026 [US3] Verify conversation history loading in backend/app/services/conversations.py — ensure load_history returns all messages ordered by created_at, and new conversations are created when conversation_id is None or invalid
- [x] T027 [US3] Add graceful handling for invalid conversation_id in backend/app/api/chat.py — if conversation_id is provided but not found in DB, create new conversation and include notice in response

**Checkpoint**: All core user stories (1-3) are independently functional. System is stateless and restart-resilient.

---

## Phase 6: User Story 4 - Bilingual Support (Priority: P4)

**Goal**: Users can interact in both English and Urdu. The agent detects language and responds appropriately.

**Independent Test**: Send Urdu task creation message, verify task created and confirmation returned in Urdu.

### Implementation for User Story 4

- [x] T028 [US4] Update agent system prompt in backend/app/agent/agent.py — add bilingual instructions: detect user language (English or Urdu), respond in the same language, handle language switching within conversations

**Checkpoint**: Bilingual support active. Agent responds in English or Urdu matching user's language.

---

## Phase 7: Frontend Integration

**Purpose**: Connect OpenAI ChatKit frontend to the backend chat endpoint

- [x] T029 Install frontend dependencies in frontend/ — @openai/chatkit-react, better-auth, and configure next.config.js
- [x] T030 Implement chat API client in frontend/src/lib/api.ts — function to call POST /api/{user_id}/chat with message and optional conversation_id, return ChatResponse
- [x] T031 Implement ChatWidget component in frontend/src/components/ChatWidget.tsx — use @openai/chatkit-react to render chat UI, wire send to api.ts, persist conversation_id in component state from response
- [x] T032 Implement chat page in frontend/src/app/page.tsx — render ChatWidget, pass user_id (hardcoded for dev or from auth)
- [x] T033 [P] Implement Better Auth client setup in frontend/src/lib/auth.ts — configure better-auth client for user authentication
- [x] T034 Add CORS middleware in backend/app/main.py — allow frontend origin (localhost:3000 in dev) to call backend API

**Checkpoint**: Full-stack integration complete. ChatKit UI sends messages to backend, displays responses, and persists conversation_id.

---

## Phase 8: Error Handling & Polish

**Purpose**: Harden error handling and cross-cutting concerns

- [x] T035 [P] Add MCP tool error standardization in backend/app/mcp/tools.py — ensure all tools return consistent error format {error: "message"} for not-found, validation, and DB errors
- [x] T036 [P] Add request validation in backend/app/api/chat.py — validate empty messages return 400 with ErrorResponse, handle DB connection errors with 500
- [x] T037 Add agent error translation in backend/app/agent/agent.py — ensure system prompt instructs agent to convert tool errors into friendly user messages
- [x] T038 Run quickstart.md validation — follow specs/001-todo-ai-chatbot/quickstart.md steps to verify setup works end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) — delivers MVP
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) — can start after or in parallel with US1
- **User Story 3 (Phase 5)**: Depends on US1 (Phase 3) — validates statelessness of existing implementation
- **User Story 4 (Phase 6)**: Depends on Foundational (Phase 2) — can start after US1
- **Frontend (Phase 7)**: Depends on US1 (Phase 3) — needs working backend endpoint
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational — No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational — Adds tools to same MCP server/agent from US1
- **User Story 3 (P3)**: Depends on US1 — Needs existing conversations to validate persistence
- **User Story 4 (P4)**: Can start after Foundational — Only modifies agent system prompt

### Within Each User Story

- MCP tools before agent definition (tools must exist for agent to use them)
- Agent definition before runner
- Runner before endpoint
- Endpoint integration last

### Parallel Opportunities

- T003 and T004 can run in parallel (different directories)
- T007, T008, T009 can run in parallel (same file but independent model classes)
- T015 and T016 can run in parallel (independent tool implementations)
- T021, T022, T023 can run in parallel (independent tool implementations)
- T029, T033 can run in parallel (different files)
- T035 and T036 can run in parallel (different files)

---

## Parallel Example: User Story 1

```bash
# Launch MCP tools in parallel (independent functions):
Task: "Implement add_task MCP tool in backend/app/mcp/tools.py"
Task: "Implement list_tasks MCP tool in backend/app/mcp/tools.py"

# Then sequentially:
Task: "Implement agent definition in backend/app/agent/agent.py"
Task: "Implement agent runner in backend/app/agent/runner.py"
Task: "Implement chat endpoint in backend/app/api/chat.py"
Task: "Register chat router in backend/app/main.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test add_task and list_tasks via curl
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready
2. Add User Story 1 -> Test independently -> MVP!
3. Add User Story 2 -> Test all 5 MCP tools -> Full CRUD
4. Add User Story 3 -> Restart test -> Stateless validated
5. Add User Story 4 -> Urdu test -> Bilingual ready
6. Add Frontend -> Full-stack integration
7. Polish -> Production ready

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All MCP tools share backend/app/mcp/tools.py but are independent functions
- Agent system prompt evolves across US1, US2, US4 (additive changes only)
