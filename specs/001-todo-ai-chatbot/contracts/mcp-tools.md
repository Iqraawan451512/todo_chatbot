# MCP Tool Contracts

**Feature**: 001-todo-ai-chatbot
**Date**: 2026-02-06

## Tool: add_task

**Description**: Creates a new task for the specified user.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["user_id", "title"],
  "properties": {
    "user_id": { "type": "string", "description": "Owner user ID" },
    "title": { "type": "string", "description": "Task title" },
    "description": { "type": "string", "description": "Optional details" }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": { "type": "integer" },
    "status": { "type": "string", "enum": ["created"] },
    "title": { "type": "string" }
  }
}
```

**Error cases**:
- Empty title: returns error message

---

## Tool: list_tasks

**Description**: Retrieves tasks for the specified user, optionally
filtered by status.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["user_id"],
  "properties": {
    "user_id": { "type": "string", "description": "Owner user ID" },
    "status": {
      "type": "string",
      "enum": ["all", "pending", "completed"],
      "default": "all",
      "description": "Filter by completion status"
    }
  }
}
```

**Output Schema**:
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "task_id": { "type": "integer" },
      "title": { "type": "string" },
      "description": { "type": "string" },
      "completed": { "type": "boolean" },
      "created_at": { "type": "string", "format": "date-time" }
    }
  }
}
```

---

## Tool: complete_task

**Description**: Marks a task as completed.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["user_id", "task_id"],
  "properties": {
    "user_id": { "type": "string", "description": "Owner user ID" },
    "task_id": { "type": "integer", "description": "Task to complete" }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": { "type": "integer" },
    "status": { "type": "string", "enum": ["completed"] },
    "title": { "type": "string" }
  }
}
```

**Error cases**:
- Task not found: returns error message
- Task already completed: returns info message

---

## Tool: delete_task

**Description**: Permanently deletes a task.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["user_id", "task_id"],
  "properties": {
    "user_id": { "type": "string", "description": "Owner user ID" },
    "task_id": { "type": "integer", "description": "Task to delete" }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": { "type": "integer" },
    "status": { "type": "string", "enum": ["deleted"] },
    "title": { "type": "string" }
  }
}
```

**Error cases**:
- Task not found: returns error message

---

## Tool: update_task

**Description**: Updates the title and/or description of a task.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["user_id", "task_id"],
  "properties": {
    "user_id": { "type": "string", "description": "Owner user ID" },
    "task_id": { "type": "integer", "description": "Task to update" },
    "title": { "type": "string", "description": "New title" },
    "description": { "type": "string", "description": "New description" }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": { "type": "integer" },
    "status": { "type": "string", "enum": ["updated"] },
    "title": { "type": "string" }
  }
}
```

**Error cases**:
- Task not found: returns error message
- No fields to update: returns info message
