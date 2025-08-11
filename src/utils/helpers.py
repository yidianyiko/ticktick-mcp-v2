"""
Helper Functions Module

Provides various general helper functions
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from utils.timezone_utils import is_task_due_today, is_task_overdue

logger = logging.getLogger(__name__)


# Common color names mapped to TickTick-compatible hex values.
COLOR_NAME_TO_HEX: dict[str, str] = {
    "red": "#FF6161",
    "pink": "#BE3B83",
    "teal": "#7CEDEB",
    "green": "#35D870",
    "yellow": "#E6EA49",
    "purple": "#C77B9B",
    "blue": "#45B7D1",
    "mint": "#96CEB4",
}


def is_hex_color(value: str) -> bool:
    """Return True if value is a #RRGGBB hex color string."""
    if not isinstance(value, str):
        return False
    if len(value) != 7 or not value.startswith("#"):
        return False
    try:
        int(value[1:], 16)
        return True
    except Exception:
        return False


def normalize_color(color: str | None) -> str | None:
    """Normalize user-provided color to a TickTick-compatible hex or None.

    - Accepts #RRGGBB directly
    - Accepts common color names (mapped above)
    - Returns None if the input is invalid or empty
    """
    if not color:
        return None
    lowered = color.strip().lower()
    if is_hex_color(lowered):
        return lowered
    mapped = COLOR_NAME_TO_HEX.get(lowered)
    if mapped:
        return mapped
    logger.warning(
        "Unrecognized project color '%s'. Defaulting to TickTick default color.",
        color,
    )
    return None


def load_credentials() -> dict[str, str] | None:
    """
    Load saved credentials

    Returns:
        Dict containing username and password, or None if not exists
    """
    config_file = Path.home() / ".ticktick-mcp" / "credentials.json"

    if not config_file.exists():
        return None

    try:
        with config_file.open() as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.exception("Error loading credentials")
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

        with config_file.open("w") as f:
            json.dump(credentials, f, indent=2)
    except Exception:
        logger.exception("Error saving credentials")
        return False
    else:
        logger.info("Credentials saved successfully")
        return True


def format_task_info(task: dict[str, Any]) -> str:
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


def format_project_info(project: dict[str, Any]) -> str:
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


def parse_date_string(date_str: str) -> datetime | None:
    """
    Parse date string into an aware datetime (UTC if naive input).

    Args:
        date_str: Date string

    Returns:
        datetime: Parsed aware datetime, or None if parsing fails
    """
    if not date_str:
        return None

    date_only_length = 10
    dash_count_for_date = 2

    try:
        normalized = date_str
        # Normalize common UTC suffixes
        if normalized.endswith("Z"):
            normalized = normalized.replace("Z", "+00:00")
        elif normalized.endswith("+0000"):
            normalized = normalized.replace("+0000", "+00:00")

        # First try ISO parser directly
        try:
            dt = datetime.fromisoformat(normalized)
        except ValueError:
            # Try to coerce to ISO shapes
            if " " in normalized and "T" not in normalized:
                # Convert space separator to 'T'
                candidate = normalized.replace(" ", "T")
                dt = datetime.fromisoformat(candidate)
            elif (
                len(normalized) == date_only_length
                and normalized.count("-") == dash_count_for_date
            ):
                # Date-only string; assume midnight
                dt = datetime.fromisoformat(normalized + "T00:00:00")
            else:
                raise

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    except ValueError:
        logger.warning("Could not parse date string: %s", date_str)
        return None
    except Exception:
        logger.exception("Error parsing date string")
        return None
    else:
        return dt


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


def filter_tasks_by_priority(
    tasks: list[dict[str, Any]], priority: int,
) -> list[dict[str, Any]]:
    """
    Filter tasks by priority

    Args:
        tasks: Task list
        priority: Priority level

    Returns:
        List: Filtered task list
    """
    return [task for task in tasks if task.get("priority") == priority]


def filter_tasks_by_status(
    tasks: list[dict[str, Any]], status: int,
) -> list[dict[str, Any]]:
    """
    Filter tasks by status

    Args:
        tasks: Task list
        status: Status value

    Returns:
        List: Filtered task list
    """
    return [task for task in tasks if task.get("status") == status]


def search_tasks(tasks: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
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


def get_tasks_due_today(
    tasks: list[dict[str, Any]], user_timezone: str = "",
) -> list[dict[str, Any]]:
    """
    Get tasks due today in user's timezone

    Args:
        tasks: Task list
        user_timezone: User's timezone string (optional, for backward compatibility)

    Returns:
        List: Tasks due today
    """
    results = []
    for task in tasks:
        if is_task_due_today(task, user_timezone):
            results.append(task)

    return results


def get_overdue_tasks(
    tasks: list[dict[str, Any]], user_timezone: str = "",
) -> list[dict[str, Any]]:
    """
    Get overdue tasks in user's timezone

    Args:
        tasks: Task list
        user_timezone: User's timezone string (optional, for backward compatibility)

    Returns:
        List: Overdue task list
    """
    results = []
    for task in tasks:
        if is_task_overdue(task, user_timezone):
            results.append(task)

    return results


def validate_task_data(task_data: dict[str, Any]) -> dict[str, Any]:
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
    title: str,
    content: str = "",
    project_id: str | None = None,
    priority: int = 0,
    due_date: str | None = None,
) -> dict[str, Any]:
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
