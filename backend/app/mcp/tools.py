"""MCP tools for todo task operations.

All task mutations go through these tools. Each tool is stateless
and interacts only with the database. No AI logic is permitted here.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session, select
from app.db.engine import engine
from app.db.models import Task
from app.mcp.server import mcp_server


@mcp_server.tool()
def add_task(user_id: str, title: str, description: Optional[str] = None) -> dict:
    """Create a new task for the user.

    Args:
        user_id: The owner's user ID.
        title: The task title (required, must not be empty).
        description: Optional task description.
    """
    if not title or not title.strip():
        return {"error": "Title cannot be empty"}

    with Session(engine) as session:
        task = Task(
            user_id=user_id,
            title=title.strip(),
            description=description,
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return {"task_id": task.id, "status": "created", "title": task.title}


@mcp_server.tool()
def list_tasks(user_id: str, status: Optional[str] = "all") -> list[dict]:
    """List tasks for the user, optionally filtered by status.

    Args:
        user_id: The owner's user ID.
        status: Filter — "all" (default), "pending", or "completed".
    """
    with Session(engine) as session:
        statement = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            statement = statement.where(Task.completed == False)
        elif status == "completed":
            statement = statement.where(Task.completed == True)

        tasks = session.exec(statement).all()
        return [
            {
                "task_id": t.id,
                "title": t.title,
                "description": t.description,
                "completed": t.completed,
                "created_at": t.created_at.isoformat(),
            }
            for t in tasks
        ]


@mcp_server.tool()
def complete_task(user_id: str, task_id: int) -> dict:
    """Mark a task as completed.

    Args:
        user_id: The owner's user ID.
        task_id: The ID of the task to complete.
    """
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if task is None or task.user_id != user_id:
            return {"error": f"Task {task_id} not found"}
        if task.completed:
            return {"task_id": task.id, "status": "already_completed", "title": task.title}
        task.completed = True
        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()
        session.refresh(task)
        return {"task_id": task.id, "status": "completed", "title": task.title}


@mcp_server.tool()
def delete_task(user_id: str, task_id: int) -> dict:
    """Delete a task permanently.

    Args:
        user_id: The owner's user ID.
        task_id: The ID of the task to delete.
    """
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if task is None or task.user_id != user_id:
            return {"error": f"Task {task_id} not found"}
        title = task.title
        session.delete(task)
        session.commit()
        return {"task_id": task_id, "status": "deleted", "title": title}


@mcp_server.tool()
def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """Update the title and/or description of a task.

    Args:
        user_id: The owner's user ID.
        task_id: The ID of the task to update.
        title: New title (optional).
        description: New description (optional).
    """
    if title is None and description is None:
        return {"error": "No fields to update. Provide title or description."}

    with Session(engine) as session:
        task = session.get(Task, task_id)
        if task is None or task.user_id != user_id:
            return {"error": f"Task {task_id} not found"}
        if title is not None:
            task.title = title.strip()
        if description is not None:
            task.description = description
        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()
        session.refresh(task)
        return {"task_id": task.id, "status": "updated", "title": task.title, "description": task.description}
