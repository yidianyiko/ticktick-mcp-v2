"""
Helper Functions Module

Provides various general helper functions
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def load_credentials() -> Optional[Dict[str, str]]:
    """
    Load saved credentials

    Returns:
        Dict containing username and password, or None if not exists
    """
    config_file = Path.home() / ".ticktick-mcp" / "credentials.json"

    if not config_file.exists():
        return None

    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading credentials: {e}")
        return None


def save_credentials(username: str, password: str) -> bool:
    """
    Save credentials to local file

    Args:
        username: Username
        password: Password

    Returns:
        bool: Whether save was successful
    """
    try:
        config_dir = Path.home() / ".ticktick-mcp"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "credentials.json"

        credentials = {"username": username, "password": password}

        with open(config_file, "w") as f:
            json.dump(credentials, f, indent=2)

        logger.info("Credentials saved successfully")
        return True

    except Exception as e:
        logger.error(f"Error saving credentials: {e}")
        return False


def format_task_info(task: Dict[str, Any]) -> str:
    """
    Format task information

    Args:
        task: Task dictionary

    Returns:
        str: Formatted task information
    """
    title = task.get("title", "Unknown")
    priority = task.get("priority", 0)
    due_date = task.get("dueDate")
    status = task.get("status", 0)

    # Priority mapping
    priority_map = {0: "None", 1: "Low", 3: "Medium", 5: "High"}
    priority_text = priority_map.get(priority, "Unknown")

    # Status mapping
    status_map = {0: "Active", 2: "Completed"}
    status_text = status_map.get(status, "Unknown")

    info = f"📋 {title}"
    info += f"\n   Priority: {priority_text}"
    info += f"\n   Status: {status_text}"

    if due_date:
        info += f"\n   Due: {due_date}"

    return info


def format_project_info(project: Dict[str, Any]) -> str:
    """
    Format project information

    Args:
        project: Project dictionary

    Returns:
        str: Formatted project information
    """
    name = project.get("name", "Unknown")
    color = project.get("color", "default")
    view_mode = project.get("viewMode", "list")

    info = f"📁 {name}"
    info += f"\n   Color: {color}"
    info += f"\n   View Mode: {view_mode}"

    return info


def parse_date_string(date_str: str) -> Optional[datetime]:
    """
    Parse date string

    Args:
        date_str: Date string

    Returns:
        datetime: Parsed date, or None if parsing fails
    """
    if not date_str:
        return None

    try:
        # Try multiple date formats
        formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        logger.warning(f"Could not parse date string: {date_str}")
        return None

    except Exception as e:
        logger.error(f"Error parsing date string: {e}")
        return None


def get_priority_level(priority: int) -> str:
    """
    Get priority level text

    Args:
        priority: Priority value

    Returns:
        str: Priority text
    """
    priority_map = {0: "None", 1: "Low", 3: "Medium", 5: "High"}
    return priority_map.get(priority, "Unknown")


def get_status_text(status: int) -> str:
    """
    Get status text

    Args:
        status: Status value

    Returns:
        str: Status text
    """
    status_map = {0: "Active", 2: "Completed"}
    return status_map.get(status, "Unknown")


def filter_tasks_by_priority(tasks: List[Dict[str, Any]], priority: int) -> List[Dict[str, Any]]:
    """
    Filter tasks by priority

    Args:
        tasks: Task list
        priority: Priority level

    Returns:
        List: Filtered task list
    """
    return [task for task in tasks if task.get("priority") == priority]


def filter_tasks_by_status(tasks: List[Dict[str, Any]], status: int) -> List[Dict[str, Any]]:
    """
    Filter tasks by status

    Args:
        tasks: Task list
        status: Status value

    Returns:
        List: Filtered task list
    """
    return [task for task in tasks if task.get("status") == status]


def search_tasks(tasks: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """
    Search tasks

    Args:
        tasks: Task list
        query: Search query

    Returns:
        List: Matching task list
    """
    if not query:
        return tasks

    query_lower = query.lower()
    results = []

    for task in tasks:
        title = task.get("title", "").lower()
        content = task.get("content", "").lower()

        if query_lower in title or query_lower in content:
            results.append(task)

    return results


def get_tasks_due_today(tasks: List[Dict[str, Any]], user_timezone: str = '') -> List[Dict[str, Any]]:
    """
    Get tasks due today in user's timezone

    Args:
        tasks: Task list
        user_timezone: User's timezone string (optional, for backward compatibility)

    Returns:
        List: Tasks due today
    """
    # Import here to avoid circular imports
    from utils.timezone_utils import is_task_due_today
    
    results = []
    for task in tasks:
        if is_task_due_today(task, user_timezone):
            results.append(task)

    return results


def get_overdue_tasks(tasks: List[Dict[str, Any]], user_timezone: str = '') -> List[Dict[str, Any]]:
    """
    Get overdue tasks in user's timezone

    Args:
        tasks: Task list
        user_timezone: User's timezone string (optional, for backward compatibility)

    Returns:
        List: Overdue task list
    """
    # Import here to avoid circular imports
    from utils.timezone_utils import is_task_overdue
    
    results = []
    for task in tasks:
        if is_task_overdue(task, user_timezone):
            results.append(task)

    return results


def validate_task_data(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate task data

    Args:
        task_data: Task data

    Returns:
        Dict: Validation result
    """
    errors = []
    warnings = []

    # Check required fields
    if not task_data.get("title"):
        errors.append("Title is required")

    # Check priority
    priority = task_data.get("priority", 0)
    if priority not in [0, 1, 3, 5]:
        warnings.append(f"Invalid priority value: {priority}")

    # Check date format
    due_date = task_data.get("dueDate")
    if due_date and not parse_date_string(due_date):
        errors.append("Invalid due date format")

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def create_task_builder(
    title: str, content: str = "", project_id: str = None, priority: int = 0, due_date: str = None
) -> Dict[str, Any]:
    """
    Create task builder

    Args:
        title: Task title
        content: Task content
        project_id: Project ID
        priority: Priority level
        due_date: Due date

    Returns:
        Dict: Task builder dictionary
    """
    task_builder = {"title": title, "content": content, "priority": priority}

    if project_id:
        task_builder["projectId"] = project_id

    if due_date:
        task_builder["dueDate"] = due_date

    return task_builder
