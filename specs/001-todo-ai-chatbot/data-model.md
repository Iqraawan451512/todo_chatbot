# Data Model: Todo AI Chatbot

**Feature**: 001-todo-ai-chatbot
**Date**: 2026-02-06

## Entities

### Task

Represents a todo item owned by a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Unique task identifier |
| user_id | String | NOT NULL, indexed | Owner's user identifier |
| title | String | NOT NULL, max 500 chars | Task title |
| description | String | NULLABLE | Optional task details |
| completed | Boolean | NOT NULL, default=False | Completion status |
| created_at | DateTime | NOT NULL, default=now() | Creation timestamp |
| updated_at | DateTime | NOT NULL, auto-update | Last modification timestamp |

**Indexes**: `idx_task_user_id` on `user_id`

**State transitions**:
- Created: `completed=False`
- Completed: `completed=True` (via `complete_task` MCP tool)
- Deleted: Row removed (via `delete_task` MCP tool)

### Conversation

Container for a sequence of messages between a user and the assistant.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Unique conversation identifier |
| user_id | String | NOT NULL, indexed | Owner's user identifier |
| created_at | DateTime | NOT NULL, default=now() | Creation timestamp |
| updated_at | DateTime | NOT NULL, auto-update | Last modification timestamp |

**Indexes**: `idx_conversation_user_id` on `user_id`

### Message

A single exchange within a conversation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, auto-increment | Unique message identifier |
| conversation_id | Integer | FK -> Conversation.id, NOT NULL | Parent conversation |
| user_id | String | NOT NULL | Owner's user identifier |
| role | String | NOT NULL, enum: "user"/"assistant" | Message author role |
| content | Text | NOT NULL | Message body |
| created_at | DateTime | NOT NULL, default=now() | Creation timestamp |

**Indexes**: `idx_message_conversation_id` on `conversation_id`

**Foreign key**: `conversation_id` references `conversations.id` with
CASCADE delete (deleting a conversation removes all its messages).

## Relationships

```text
User (external, identified by user_id string)
 ├── has many Tasks
 └── has many Conversations
      └── has many Messages
```

- A user can have many tasks (independent of conversations)
- A user can have many conversations
- A conversation has many messages, ordered by `created_at`
- Tasks and conversations are independent entities (no FK between them)

## Validation Rules

- `title` MUST NOT be empty or whitespace-only
- `role` MUST be one of: "user", "assistant"
- `user_id` MUST NOT be empty
- `conversation_id` on Message MUST reference an existing Conversation

## Migration Strategy

- Use SQLModel's `SQLModel.metadata.create_all(engine)` for initial
  schema creation
- For production migrations, use Alembic with SQLModel models as the
  source of truth
