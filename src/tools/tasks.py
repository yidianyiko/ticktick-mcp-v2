"""
Task Management Tools
Task management MCP tools based on ticktick.py library
"""

import logging
from datetime import datetime
from typing import Any

from adapters.client import get_client
from utils.timezone_utils import (
    convert_task_times_to_local,
    convert_tasks_times_to_local,
)

logger = logging.getLogger(__name__)


def get_tasks(include_completed: bool = False) -> list[dict[str, Any]]:
    """Get all tasks list"""
    try:
        adapter = get_client()
        tasks = adapter.get_tasks(include_completed)

        # Convert UTC times to local times
        tasks = convert_tasks_times_to_local(tasks)

        logger.info("Retrieved %d tasks", len(tasks))

        return tasks
    except Exception:
        logger.exception("Error getting tasks")
        return []


def create_task(
    title: str,
    project_id: str | None = None,
    content: str | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
    priority: int = 0,
) -> dict[str, Any]:
    """
    Create new task with proper date handling.

    Args:
        title: Task title
        project_id: Optional project ID
        content: Optional task content/description
        start_date: Optional start date in format "YYYY-MM-DD HH:MM:SS" (24-hour format)
        due_date: Optional due date in format "YYYY-MM-DD HH:MM:SS" (24-hour format)
        priority: Task priority (0=None, 1=Low, 3=Medium, 5=High)

    Returns:
        Created task dictionary

    Example:
        create_task(
            title="Meeting with team",
            start_date="2024-12-28 20:05:00",
            due_date="2024-12-28 22:05:00"
        )
    """
    try:
        adapter = get_client()

        # Parse and validate date strings if provided
        dt_start = None
        dt_due = None

        if start_date:
            try:
                dt_start = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                msg = f"Invalid start_date format. Expected 'YYYY-MM-DD HH:MM:SS', got '{start_date}'"
                raise ValueError(msg)

        if due_date:
            try:
                dt_due = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                msg = f"Invalid due_date format. Expected 'YYYY-MM-DD HH:MM:SS', got '{due_date}'"
                raise ValueError(msg)

        # Get user's timezone from TickTick client (fallback to system timezone)
        user_timezone = adapter._get_user_timezone()
        if not user_timezone:
            # Fallback to Asia/Shanghai if no timezone found
            user_timezone = "Asia/Shanghai"
            logger.info("Using fallback timezone: %s", user_timezone)
        else:
            logger.info("Using user timezone: %s", user_timezone)

        # Use ticktick.py's builder method for proper date formatting
        task = adapter.create_task_with_dates(
            title=title,
            project_id=project_id,
            content=content,
            start_date=dt_start,
            due_date=dt_due,
            priority=priority,
            timezone=user_timezone,
        )

        # Convert UTC times to local times for display
        task = convert_task_times_to_local(task)

        logger.info("Created task: %s", title)
        return task
    except Exception:
        logger.exception("Error creating task")
        raise


def update_task(
    task_id: str,
    project_id: str | None = None,
    title: str | None = None,
    content: str | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
    priority: int | None = None,
) -> dict[str, Any]:
    """
    Update existing task with proper date handling.

    Args:
        task_id: ID of the task to update
        project_id: Optional project ID
        title: Optional new task title
        content: Optional new task content/description
        start_date: Optional new start date in format "YYYY-MM-DD HH:MM:SS" (24-hour format)
        due_date: Optional new due date in format "YYYY-MM-DD HH:MM:SS" (24-hour format)
        priority: Optional new task priority (0=None, 1=Low, 3=Medium, 5=High)

    Returns:
        Updated task dictionary
    """
    try:
        adapter = get_client()

        # Parse and validate date strings if provided
        dt_start = None
        dt_due = None

        if start_date:
            try:
                dt_start = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                msg = f"Invalid start_date format. Expected 'YYYY-MM-DD HH:MM:SS', got '{start_date}'"
                raise ValueError(msg)

        if due_date:
            try:
                dt_due = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                msg = f"Invalid due_date format. Expected 'YYYY-MM-DD HH:MM:SS', got '{due_date}'"
                raise ValueError(msg)

        # Get user's timezone
        user_timezone = adapter._get_user_timezone()
        if not user_timezone:
            user_timezone = "Asia/Shanghai"

        # Use the adapter's update method with proper date handling
        task = adapter.update_task_with_dates(
            task_id=task_id,
            project_id=project_id,
            title=title,
            content=content,
            start_date=dt_start,
            due_date=dt_due,
            priority=priority,
            timezone=user_timezone,
        )

        # Convert UTC times to local times
        task = convert_task_times_to_local(task)

        logger.info("Updated task: %s", task_id)
        return task
    except Exception:
        logger.exception("Error updating task")
        raise


def delete_task(project_id: str, task_id: str) -> bool:
    """Delete task"""
    try:
        adapter = get_client()

        result = adapter.delete_task(project_id, task_id)

        logger.info("Deleted task: %s", task_id)
        return result
    except Exception:
        logger.exception("Error deleting task")
        raise


def complete_task(task_id: str) -> bool:
    """Mark task as completed"""
    try:
        adapter = get_client()

        result = adapter.complete_task(task_id)

        logger.info("Completed task: %s", task_id)
        return result
    except Exception:
        logger.exception("Error completing task")
        raise


def search_tasks(query: str) -> list[dict[str, Any]]:
    """Search tasks by query"""
    try:
        adapter = get_client()
        tasks = adapter.search_tasks(query)

        # Convert UTC times to local times
        tasks = convert_tasks_times_to_local(tasks)

        logger.info("Found %d tasks matching query: %s", len(tasks), query)
        return tasks
    except Exception:
        logger.exception("Error searching tasks")
        return []


def get_tasks_by_priority(priority: int) -> list[dict[str, Any]]:
    """Get tasks by priority level"""
    try:
        adapter = get_client()
        tasks = adapter.get_tasks_by_priority(priority)

        # Convert UTC times to local times
        tasks = convert_tasks_times_to_local(tasks)

        logger.info("Found %d tasks with priority %s", len(tasks), priority)
        return tasks
    except Exception:
        logger.exception("Error getting tasks by priority")
        return []


def get_tasks_due_today() -> list[dict[str, Any]]:
    """Get tasks due today"""
    try:
        adapter = get_client()
        tasks = adapter.get_tasks_due_today()

        # Convert UTC times to local times
        tasks = convert_tasks_times_to_local(tasks)

        logger.info("Found %d tasks due today", len(tasks))
        return tasks
    except Exception:
        logger.exception("Error getting tasks due today")
        return []


def get_overdue_tasks() -> list[dict[str, Any]]:
    """Get overdue tasks"""
    try:
        adapter = get_client()
        tasks = adapter.get_overdue_tasks()

        # Convert UTC times to local times
        tasks = convert_tasks_times_to_local(tasks)

        logger.info("Found %d overdue tasks", len(tasks))
        return tasks
    except Exception:
        logger.exception("Error getting overdue tasks")
        return []
