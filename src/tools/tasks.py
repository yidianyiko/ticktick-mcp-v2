"""
Task Management Tools
Task management MCP tools based on ticktick.py library
"""

import logging
from typing import Any, Dict, List, Optional

from adapters.client import get_client
from utils.timezone_utils import convert_tasks_times_to_local, convert_task_times_to_local

logger = logging.getLogger(__name__)


def get_tasks(include_completed: bool = False) -> List[Dict[str, Any]]:
    """Get all tasks list"""
    try:
        adapter = get_client()
        tasks = adapter.get_tasks(include_completed)

        # Convert UTC times to local times
        tasks = convert_tasks_times_to_local(tasks)

        logger.info(f"Retrieved {len(tasks)} tasks")

        return tasks
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return []


def create_task(
    title: str,
    project_id: Optional[str] = None,
    content: Optional[str] = None,
    start_date: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: int = 0,
) -> Dict[str, Any]:
    """Create new task"""
    try:
        adapter = get_client()

        # Prepare task data
        task_data = {"title": title, "priority": priority}

        # Only add projectId if provided
        if project_id:
            task_data["projectId"] = project_id

        if content:
            task_data["content"] = content
        if start_date:
            task_data["startDate"] = start_date
        if due_date:
            task_data["dueDate"] = due_date

        task = adapter.create_task(**task_data)

        # Convert UTC times to local times
        task = convert_task_times_to_local(task)

        logger.info(f"Created task: {title}")
        return task
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise


def update_task(
    task_id: str,
    project_id: Optional[str] = None,
    title: Optional[str] = None,
    content: Optional[str] = None,
    start_date: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[int] = None,
) -> Dict[str, Any]:
    """Update existing task"""
    try:
        adapter = get_client()

        # Prepare update data
        update_data = {}
        if title:
            update_data["title"] = title
        if content:
            update_data["content"] = content
        if start_date:
            update_data["startDate"] = start_date
        if due_date:
            update_data["dueDate"] = due_date
        if priority is not None:
            update_data["priority"] = priority

        task = adapter.update_task(task_id, project_id, **update_data)

        # Convert UTC times to local times
        task = convert_task_times_to_local(task)

        logger.info(f"Updated task: {task_id}")
        return task
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise


def delete_task(project_id: str, task_id: str) -> bool:
    """Delete task"""
    try:
        adapter = get_client()

        result = adapter.delete_task(project_id, task_id)

        logger.info(f"Deleted task: {task_id}")
        return result
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise


def complete_task(task_id: str) -> bool:
    """Mark task as completed"""
    try:
        adapter = get_client()

        result = adapter.complete_task(task_id)

        logger.info(f"Completed task: {task_id}")
        return result
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        raise


def search_tasks(query: str) -> List[Dict[str, Any]]:
    """Search tasks by query"""
    try:
        adapter = get_client()
        tasks = adapter.search_tasks(query)

        # Convert UTC times to local times
        tasks = convert_tasks_times_to_local(tasks)

        logger.info(f"Found {len(tasks)} tasks matching query: {query}")
        return tasks
    except Exception as e:
        logger.error(f"Error searching tasks: {e}")
        return []


def get_tasks_by_priority(priority: int) -> List[Dict[str, Any]]:
    """Get tasks by priority level"""
    try:
        adapter = get_client()
        tasks = adapter.get_tasks_by_priority(priority)

        # Convert UTC times to local times
        tasks = convert_tasks_times_to_local(tasks)

        logger.info(f"Found {len(tasks)} tasks with priority {priority}")
        return tasks
    except Exception as e:
        logger.error(f"Error getting tasks by priority: {e}")
        return []


def get_tasks_due_today() -> List[Dict[str, Any]]:
    """Get tasks due today"""
    try:
        adapter = get_client()
        tasks = adapter.get_tasks_due_today()

        # Convert UTC times to local times
        tasks = convert_tasks_times_to_local(tasks)

        logger.info(f"Found {len(tasks)} tasks due today")
        return tasks
    except Exception as e:
        logger.error(f"Error getting tasks due today: {e}")
        return []


def get_overdue_tasks() -> List[Dict[str, Any]]:
    """Get overdue tasks"""
    try:
        adapter = get_client()
        tasks = adapter.get_overdue_tasks()

        # Convert UTC times to local times
        tasks = convert_tasks_times_to_local(tasks)

        logger.info(f"Found {len(tasks)} overdue tasks")
        return tasks
    except Exception as e:
        logger.error(f"Error getting overdue tasks: {e}")
        return []
