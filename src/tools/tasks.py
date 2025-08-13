"""
Task Management Tools
Task management MCP tools based on ticktick.py library
"""

import logging
from datetime import datetime, timezone
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
    except Exception:
        logger.exception("Error getting tasks")
        return []
    else:
        # Convert UTC times to local times
        tasks = convert_tasks_times_to_local(tasks)

        logger.info("Retrieved %d tasks", len(tasks))

        return tasks


def create_task(
    title: str,
    project_id: str | None = None,
    content: str | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
    priority: int = 0,
) -> dict[str, Any]:
    """
    Create a new task by delegating to the adapter's appropriate create API.

    Notes:
    - Uses date-aware method when time parameters are provided
    - Filters out parameters that are None, but preserves empty strings
    - Maps snake_case parameters to TickTick field names expected by tests
    """
    try:
        adapter = get_client()

        # If we have time parameters, use the date-aware method
        if start_date is not None or due_date is not None:
            from datetime import datetime
            
            # Parse start_date and due_date to datetime objects
            start_datetime = None
            due_datetime = None
            
            if start_date is not None:
                try:
                    start_datetime = datetime.fromisoformat(start_date.replace(' ', 'T'))
                except ValueError:
                    logger.warning("Invalid start_date format: %s, expected 'YYYY-MM-DD HH:MM:SS'", start_date)
                    
            if due_date is not None:
                try:
                    due_datetime = datetime.fromisoformat(due_date.replace(' ', 'T'))
                except ValueError:
                    logger.warning("Invalid due_date format: %s, expected 'YYYY-MM-DD HH:MM:SS'", due_date)
            
            # Get user's timezone from TickTick client
            user_timezone = adapter.get_user_timezone()
            if not user_timezone:
                user_timezone = "Asia/Shanghai"  # Fallback timezone
                logger.warning("Could not get user timezone, using fallback: %s", user_timezone)
            
            # Use the date-aware method
            task = adapter.create_task_with_dates(
                title=title,
                project_id=project_id,
                content=content,
                start_date=start_datetime,
                due_date=due_datetime,
                priority=priority,
                timezone=user_timezone
            )
        else:
            # Use simple method for tasks without dates
            create_kwargs: dict[str, Any] = {"title": title, "priority": priority}
            if content is not None:
                create_kwargs["content"] = content
            if project_id is not None:
                create_kwargs["projectId"] = project_id

            task = adapter.create_task(**create_kwargs)

        # Convert UTC times to local times for display
        task = convert_task_times_to_local(task)
    except Exception as err:
        logger.exception("Error creating task")
        msg = "Failed to create task"
        raise RuntimeError(msg) from err
    else:
        logger.info("Created task: %s", title)
        return task


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
    Update an existing task via the adapter's appropriate update API.

    Notes:
    - Uses date-aware method when time parameters are provided
    - Filters out None values; includes zero and empty strings
    - Maps snake_case parameters to expected TickTick field names
    """
    try:
        adapter = get_client()

        # If we have time parameters, use the date-aware method
        if start_date is not None or due_date is not None:
            from datetime import datetime
            
            # Parse start_date and due_date to datetime objects
            start_datetime = None
            due_datetime = None
            
            if start_date is not None:
                try:
                    start_datetime = datetime.fromisoformat(start_date.replace(' ', 'T'))
                except ValueError:
                    logger.warning("Invalid start_date format: %s, expected 'YYYY-MM-DD HH:MM:SS'", start_date)
                    
            if due_date is not None:
                try:
                    due_datetime = datetime.fromisoformat(due_date.replace(' ', 'T'))
                except ValueError:
                    logger.warning("Invalid due_date format: %s, expected 'YYYY-MM-DD HH:MM:SS'", due_date)
            
            # Get user's timezone from TickTick client
            user_timezone = adapter.get_user_timezone()
            if not user_timezone:
                user_timezone = "Asia/Shanghai"  # Fallback timezone
                logger.warning("Could not get user timezone, using fallback: %s", user_timezone)
            
            # Use the date-aware method
            task = adapter.update_task_with_dates(
                task_id=task_id,
                project_id=project_id,
                title=title,
                content=content,
                start_date=start_datetime,
                due_date=due_datetime,
                priority=priority,
                timezone=user_timezone
            )
        else:
            # Use simple method for updates without dates
            update_kwargs: dict[str, Any] = {}
            if title is not None:
                update_kwargs["title"] = title
            if content is not None:
                update_kwargs["content"] = content
            if priority is not None:
                update_kwargs["priority"] = priority

            # Call adapter.update_task ensuring the second positional argument is project_id
            task = adapter.update_task(task_id, project_id, **update_kwargs)
    except Exception as err:
        logger.exception("Error updating task")
        msg = "Failed to update task"
        raise RuntimeError(msg) from err
    else:
        task = convert_task_times_to_local(task)
        logger.info("Updated task: %s", task_id)
        return task


def delete_task(task_id: str) -> bool:
    """Delete a task by its task_id.
    """
    try:
        adapter = get_client()
        # Pass None for project_id to indicate it's intentionally unused
        result = adapter.delete_task(None, task_id)
    except Exception as err:
        logger.exception("Error deleting task")
        msg = "Failed to delete task"
        raise RuntimeError(msg) from err
    else:
        logger.info("Deleted task: %s", task_id)
        return result


def complete_task(task_id: str) -> bool:
    """Mark task as completed"""
    try:
        adapter = get_client()
        result = adapter.complete_task(task_id)
    except Exception as err:
        logger.exception("Error completing task")
        msg = "Failed to complete task"
        raise RuntimeError(msg) from err
    else:
        logger.info("Completed task: %s", task_id)
        return result


def search_tasks(query: str) -> list[dict[str, Any]]:
    """Search tasks by query"""
    try:
        adapter = get_client()
        tasks = adapter.search_tasks(query)
    except Exception:
        logger.exception("Error searching tasks")
        return []
    else:
        # Convert UTC times to local times
        tasks = convert_tasks_times_to_local(tasks)

        logger.info("Found %d tasks matching query: %s", len(tasks), query)
        return tasks


def get_tasks_by_priority(priority: int) -> list[dict[str, Any]]:
    """Get tasks by priority level"""
    try:
        adapter = get_client()
        tasks = adapter.get_tasks_by_priority(priority)
    except Exception:
        logger.exception("Error getting tasks by priority")
        return []
    else:
        # Convert UTC times to local times
        tasks = convert_tasks_times_to_local(tasks)

        logger.info("Found %d tasks with priority %s", len(tasks), priority)
        return tasks


def get_tasks_due_today() -> list[dict[str, Any]]:
    """Get tasks due today"""
    try:
        adapter = get_client()
        tasks = adapter.get_tasks_due_today()
    except Exception:
        logger.exception("Error getting tasks due today")
        return []
    else:
        # Convert UTC times to local times
        tasks = convert_tasks_times_to_local(tasks)

        logger.info("Found %d tasks due today", len(tasks))
        return tasks


def get_overdue_tasks() -> list[dict[str, Any]]:
    """Get overdue tasks"""
    try:
        adapter = get_client()
        tasks = adapter.get_overdue_tasks()
    except Exception:
        logger.exception("Error getting overdue tasks")
        return []
    else:
        # Convert UTC times to local times
        tasks = convert_tasks_times_to_local(tasks)

        logger.info("Found %d overdue tasks", len(tasks))
        return tasks
