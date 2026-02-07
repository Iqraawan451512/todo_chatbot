"""TaskAgent — Executes MCP tool calls based on parsed intent.

This agent ONLY performs tool execution. No reasoning, no language
detection, no response formatting. All task mutations go through
MCP tools exclusively.

This agent is stateless, reusable, and independent of other agents.
"""
from dataclasses import dataclass, field
from app.mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task
from app.agent.intent_agent import IntentResult


@dataclass
class TaskResult:
    """Result of MCP tool execution."""
    success: bool
    data: dict | list = field(default_factory=dict)
    tool_calls: list[dict] = field(default_factory=list)
    error: str | None = None


def execute_task(user_id: str, intent: IntentResult) -> TaskResult:
    """Execute the appropriate MCP tool based on the parsed intent.

    Args:
        user_id: The authenticated user's ID.
        intent: The parsed intent from IntentAgent.

    Returns:
        TaskResult with execution outcome and tool call records.
    """
    tool_calls: list[dict] = []

    if intent.intent == "add":
        return _handle_add(user_id, intent, tool_calls)
    elif intent.intent == "list":
        return _handle_list(user_id, intent, tool_calls)
    elif intent.intent == "complete":
        return _handle_complete(user_id, intent, tool_calls)
    elif intent.intent == "delete":
        return _handle_delete(user_id, intent, tool_calls)
    elif intent.intent == "update":
        return _handle_update(user_id, intent, tool_calls)

    return TaskResult(success=False, error="unknown_intent", tool_calls=tool_calls)


def _handle_add(user_id: str, intent: IntentResult, tool_calls: list[dict]) -> TaskResult:
    if not intent.title:
        return TaskResult(success=False, error="missing_title", tool_calls=tool_calls)

    result = add_task(user_id=user_id, title=intent.title, description=intent.description)
    args: dict = {"user_id": user_id, "title": intent.title}
    if intent.description:
        args["description"] = intent.description
    tool_calls.append({"tool": "add_task", "arguments": args, "result": result})

    if "error" in result:
        return TaskResult(success=False, data=result, error=result["error"], tool_calls=tool_calls)
    return TaskResult(success=True, data=result, tool_calls=tool_calls)


def _handle_list(user_id: str, intent: IntentResult, tool_calls: list[dict]) -> TaskResult:
    status = intent.status_filter
    result = list_tasks(user_id=user_id, status=status)
    tool_calls.append({"tool": "list_tasks", "arguments": {"user_id": user_id, "status": status}, "result": result})

    return TaskResult(success=True, data=result, tool_calls=tool_calls)


def _handle_complete(user_id: str, intent: IntentResult, tool_calls: list[dict]) -> TaskResult:
    if intent.task_id is None:
        return TaskResult(success=False, error="missing_task_id", tool_calls=tool_calls)

    result = complete_task(user_id=user_id, task_id=intent.task_id)
    tool_calls.append({"tool": "complete_task", "arguments": {"user_id": user_id, "task_id": intent.task_id}, "result": result})

    if "error" in result:
        return TaskResult(success=False, data=result, error=result["error"], tool_calls=tool_calls)
    return TaskResult(success=True, data=result, tool_calls=tool_calls)


def _handle_delete(user_id: str, intent: IntentResult, tool_calls: list[dict]) -> TaskResult:
    if intent.task_id is None:
        return TaskResult(success=False, error="missing_task_id", tool_calls=tool_calls)

    result = delete_task(user_id=user_id, task_id=intent.task_id)
    tool_calls.append({"tool": "delete_task", "arguments": {"user_id": user_id, "task_id": intent.task_id}, "result": result})

    if "error" in result:
        return TaskResult(success=False, data=result, error=result["error"], tool_calls=tool_calls)
    return TaskResult(success=True, data=result, tool_calls=tool_calls)


def _handle_update(user_id: str, intent: IntentResult, tool_calls: list[dict]) -> TaskResult:
    if intent.task_id is None:
        return TaskResult(success=False, error="missing_task_id", tool_calls=tool_calls)

    if not intent.update_value:
        return TaskResult(
            success=False,
            error="missing_update_value",
            data={"update_field": intent.update_field or "title"},
            tool_calls=tool_calls,
        )

    if intent.update_field == "description":
        result = update_task(user_id=user_id, task_id=intent.task_id, description=intent.update_value)
        tool_calls.append({"tool": "update_task", "arguments": {"user_id": user_id, "task_id": intent.task_id, "description": intent.update_value}, "result": result})
    else:
        result = update_task(user_id=user_id, task_id=intent.task_id, title=intent.update_value)
        tool_calls.append({"tool": "update_task", "arguments": {"user_id": user_id, "task_id": intent.task_id, "title": intent.update_value}, "result": result})

    if "error" in result:
        return TaskResult(success=False, data=result, error=result["error"], tool_calls=tool_calls)
    return TaskResult(success=True, data=result, tool_calls=tool_calls)
