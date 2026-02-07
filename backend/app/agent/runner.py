"""Agent execution logic.

Uses keyword-based intent parsing to call MCP tool functions directly.
No external AI API required — all operations go through the database.
"""
import re
from dataclasses import dataclass, field
from app.mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task


@dataclass
class AgentResult:
    response: str
    tool_calls: list[dict] = field(default_factory=list)


def _parse_task_id(message: str) -> int | None:
    """Extract a task ID number from the message."""
    match = re.search(r'\btask\s*#?\s*(\d+)\b', message, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # Try standalone number
    match = re.search(r'\b(\d+)\b', message)
    if match:
        return int(match.group(1))
    return None


def _extract_title(message: str, keywords: list[str]) -> str:
    """Extract task title by removing the command keyword."""
    lower = message.lower()
    for kw in keywords:
        idx = lower.find(kw)
        if idx != -1:
            title = message[idx + len(kw):].strip()
            # Clean up common filler words at the start
            for filler in ["a task to ", "a task ", "task to ", "task ", "to "]:
                if title.lower().startswith(filler):
                    title = title[len(filler):]
                    break
            return title.strip().strip("'\"")
    return message.strip().strip("'\"")


def _parse_title_and_description(raw: str) -> tuple[str, str | None]:
    """Split raw text into (title, description).

    Handles formats like:
      "Buy milk" with description "from the store"
      Buy milk with description from the store
      "Buy milk"
      Buy milk
    """
    # Try: "title" with description "desc"
    match = re.match(
        r'^["\']?(.+?)["\']?\s+with\s+description\s+["\']?(.+?)["\']?\s*$',
        raw, re.IGNORECASE,
    )
    if match:
        return match.group(1).strip(), match.group(2).strip()

    # No description — clean up quotes from the title
    title = raw.strip().strip("'\"")
    return title, None


# Regex fragment matching "description" and common misspellings
_DESC_KW = r'(?:desc|disc)(?:r?(?:i|u)ption|ription|ruption)?'


def _is_description_update(lower_message: str) -> bool:
    """Check if the message refers to a description update.

    Handles misspellings: description, discription, discruption, desc, etc.
    """
    return bool(re.search(r'\b' + _DESC_KW + r'\b', lower_message))


def _detect_intent(message: str) -> str:
    """Detect user intent from the message."""
    lower = message.lower().strip()

    # Check for completion intent
    if any(kw in lower for kw in ["complete", "mark", "done", "finish"]):
        return "complete"

    # Check for delete intent
    if any(kw in lower for kw in ["delete", "remove"]):
        return "delete"

    # Check for update intent
    if any(kw in lower for kw in ["update", "change", "rename", "edit"]):
        return "update"

    # Check for list intent
    if any(kw in lower for kw in ["show", "list", "all my", "what", "pending", "incomplete", "completed"]):
        return "list"

    # Check for add intent
    if any(kw in lower for kw in ["add", "create", "remember", "save", "new task"]):
        return "add"

    # Default: treat as add task
    return "add"


def _detect_status_filter(message: str) -> str:
    """Detect list filter from message."""
    lower = message.lower()
    if any(kw in lower for kw in ["pending", "incomplete", "not done", "remaining"]):
        return "pending"
    if any(kw in lower for kw in ["completed", "done", "finished"]):
        return "completed"
    return "all"


async def run_agent(
    user_id: str,
    conversation_history: list[dict],
    user_message: str,
) -> AgentResult:
    """Process user message with keyword parsing and call MCP tools directly.

    Args:
        user_id: The authenticated user's ID.
        conversation_history: Prior messages (unused in keyword mode).
        user_message: The new user message to process.

    Returns:
        AgentResult with the response and tool calls made.
    """
    intent = _detect_intent(user_message)
    tool_calls = []

    if intent == "add":
        raw = _extract_title(user_message, ["add", "create", "remember", "save", "new task"])
        if not raw:
            return AgentResult(response="Please provide a task title. Example: 'Add a task to buy groceries'")

        # Parse title and optional description from the raw extracted text
        title, description = _parse_title_and_description(raw)

        if not title:
            return AgentResult(response="Please provide a task title. Example: 'Add a task to buy groceries'")

        result = add_task(user_id=user_id, title=title, description=description)
        args: dict = {"user_id": user_id, "title": title}
        if description:
            args["description"] = description
        tool_calls.append({"tool": "add_task", "arguments": args, "result": result})

        if "error" in result:
            return AgentResult(response=f"Could not add task: {result['error']}", tool_calls=tool_calls)
        resp = f"Added task '{result['title']}' (ID: {result['task_id']})"
        if description:
            resp += f" with description: {description}"
        return AgentResult(response=resp, tool_calls=tool_calls)

    elif intent == "list":
        status = _detect_status_filter(user_message)
        result = list_tasks(user_id=user_id, status=status)
        tool_calls.append({"tool": "list_tasks", "arguments": {"user_id": user_id, "status": status}, "result": result})

        if not result:
            filter_text = f" {status}" if status != "all" else ""
            return AgentResult(response=f"You have no{filter_text} tasks.", tool_calls=tool_calls)

        lines = []
        for t in result:
            check = "done" if t["completed"] else "pending"
            line = f"  {t['task_id']}. {t['title']} [{check}]"
            if t.get("description"):
                line += f"\n      Description: {t['description']}"
            lines.append(line)
        header = f"Your tasks ({status}):" if status != "all" else "Your tasks:"
        return AgentResult(response=f"{header}\n" + "\n".join(lines), tool_calls=tool_calls)

    elif intent == "complete":
        task_id = _parse_task_id(user_message)
        if task_id is None:
            return AgentResult(response="Please specify a task ID. Example: 'Complete task 3'")

        result = complete_task(user_id=user_id, task_id=task_id)
        tool_calls.append({"tool": "complete_task", "arguments": {"user_id": user_id, "task_id": task_id}, "result": result})

        if "error" in result:
            return AgentResult(response=f"Could not complete task: {result['error']}", tool_calls=tool_calls)
        if result.get("status") == "already_completed":
            return AgentResult(response=f"Task '{result['title']}' is already completed.", tool_calls=tool_calls)
        return AgentResult(response=f"Marked task '{result['title']}' as complete!", tool_calls=tool_calls)

    elif intent == "delete":
        task_id = _parse_task_id(user_message)
        if task_id is None:
            return AgentResult(response="Please specify a task ID. Example: 'Delete task 2'")

        result = delete_task(user_id=user_id, task_id=task_id)
        tool_calls.append({"tool": "delete_task", "arguments": {"user_id": user_id, "task_id": task_id}, "result": result})

        if "error" in result:
            return AgentResult(response=f"Could not delete task: {result['error']}", tool_calls=tool_calls)
        return AgentResult(response=f"Deleted task '{result['title']}'.", tool_calls=tool_calls)

    elif intent == "update":
        task_id = _parse_task_id(user_message)
        if task_id is None:
            return AgentResult(response="Please specify a task ID. Example: 'Update task 1 title to Call mom'")

        lower = user_message.lower()
        is_description = _is_description_update(lower)

        new_value = None

        if is_description:
            # Find the description keyword and extract value after it
            # Supports: "description to X", "description with X", "description X"
            # Also handles misspellings like discription, discruption, desc
            desc_match = re.search(
                r'\b' + _DESC_KW + r'\s+(?:to\s+|with\s+)?["\']?(.+?)["\']?\s*$',
                user_message, re.IGNORECASE,
            )
            if desc_match:
                new_value = desc_match.group(1).strip().strip("'\"")
        else:
            # Title update: extract after "title to/with" or just "to/with"
            title_match = re.search(r'\btitle\s+(?:to|with)\s+["\']?(.+?)["\']?\s*$', user_message, re.IGNORECASE)
            if title_match:
                new_value = title_match.group(1).strip().strip("'\"")
            else:
                title_match = re.search(r'\b(?:to|with)\s+["\']?(.+?)["\']?\s*$', user_message, re.IGNORECASE)
                if title_match:
                    new_value = title_match.group(1).strip().strip("'\"")

        if not new_value:
            if is_description:
                return AgentResult(response="Please provide the new description. Example: 'Update task 1 description to My new description'")
            return AgentResult(response="Please provide the new title. Example: 'Update task 1 title to New title'")

        if is_description:
            result = update_task(user_id=user_id, task_id=task_id, description=new_value)
            tool_calls.append({"tool": "update_task", "arguments": {"user_id": user_id, "task_id": task_id, "description": new_value}, "result": result})
        else:
            result = update_task(user_id=user_id, task_id=task_id, title=new_value)
            tool_calls.append({"tool": "update_task", "arguments": {"user_id": user_id, "task_id": task_id, "title": new_value}, "result": result})

        if "error" in result:
            return AgentResult(response=f"Could not update task: {result['error']}", tool_calls=tool_calls)

        if is_description:
            return AgentResult(response=f"Updated description for task {task_id} to: {result.get('description', new_value)}", tool_calls=tool_calls)
        return AgentResult(response=f"Updated task title to '{result['title']}'.", tool_calls=tool_calls)

    return AgentResult(response="I didn't understand that. Try: 'Add buy groceries', 'Show my tasks', 'Complete task 1', 'Delete task 2'")
