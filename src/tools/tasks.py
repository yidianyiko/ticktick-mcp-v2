"""
Task Management Tools
Task management MCP tools based on ticktick.py library
"""

import logging
from datetime import datetime
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
                raise ValueError(f"Invalid start_date format. Expected 'YYYY-MM-DD HH:MM:SS', got '{start_date}'")
        
        if due_date:
            try:
                dt_due = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError(f"Invalid due_date format. Expected 'YYYY-MM-DD HH:MM:SS', got '{due_date}'")

        # Get user's timezone from TickTick client (fallback to system timezone)
        user_timezone = adapter._get_user_timezone()
        if not user_timezone:
            # Fallback to Asia/Shanghai if no timezone found
            user_timezone = "Asia/Shanghai"
            logger.info(f"Using fallback timezone: {user_timezone}")
        else:
            logger.info(f"Using user timezone: {user_timezone}")

        # Use ticktick.py's builder method for proper date formatting
        task = adapter.create_task_with_dates(
            title=title,
            project_id=project_id,
            content=content,
            start_date=dt_start,
            due_date=dt_due,
            priority=priority,
            timezone=user_timezone
        )

        # Convert UTC times to local times for display
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
                raise ValueError(f"Invalid start_date format. Expected 'YYYY-MM-DD HH:MM:SS', got '{start_date}'")
        
        if due_date:
            try:
                dt_due = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError(f"Invalid due_date format. Expected 'YYYY-MM-DD HH:MM:SS', got '{due_date}'")

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
            timezone=user_timezone
        )

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
