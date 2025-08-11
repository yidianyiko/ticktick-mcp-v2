"""
Timezone conversion utilities for TickTick MCP tools
"""

import logging
from datetime import date, datetime, timezone
from typing import Any

import pytz

logger = logging.getLogger(__name__)

# TickTick status constants
COMPLETED_STATUS = 2


def convert_utc_to_local_time(utc_time_str: str, timezone_str: str) -> str:
    """
    Convert UTC time string to local time string based on timezone

    Args:
        utc_time_str: UTC time string in format like "2025-08-01T16:00:00.000+0000"
        timezone_str: Timezone string like "Asia/Shanghai"

    Returns:
        Local time string in format like "2025-08-02T00:00:00"
    """
    try:
        # Parse UTC time string
        if utc_time_str.endswith("Z"):
            utc_time_str = utc_time_str.replace("Z", "+00:00")
        elif utc_time_str.endswith("+0000"):
            utc_time_str = utc_time_str.replace("+0000", "+00:00")

        # Parse the datetime
        utc_dt = datetime.fromisoformat(utc_time_str)

        # Get timezone
        if timezone_str and timezone_str.strip():
            tz = pytz.timezone(timezone_str)
            # Convert to local time
            local_dt = utc_dt.astimezone(tz)
            # Format as local time string (without timezone info for user-friendly display)
            return local_dt.strftime("%Y-%m-%dT%H:%M:%S")
        # If no timezone info, return UTC time as is
        return utc_dt.strftime("%Y-%m-%dT%H:%M:%S")

    except (ValueError, TypeError, pytz.UnknownTimeZoneError) as e:
        logger.debug(
            "Failed to convert time %s with timezone %s: %s",
            utc_time_str,
            timezone_str,
            e,
        )
        return utc_time_str


def convert_task_times_to_local(task: dict[str, Any]) -> dict[str, Any]:
    """
    Convert all time fields in a task from UTC to local time

    Args:
        task: Task dictionary containing time fields and timezone info

    Returns:
        Task dictionary with converted local times
    """
    try:
        # Get timezone from task
        timezone_str = task.get("timeZone", "")

        # Convert startDate if present
        if task.get("startDate"):
            task["startDate"] = convert_utc_to_local_time(
                task["startDate"], timezone_str,
            )

        # Convert dueDate if present
        if task.get("dueDate"):
            task["dueDate"] = convert_utc_to_local_time(task["dueDate"], timezone_str)

        # Convert modifiedTime if present
        if task.get("modifiedTime"):
            task["modifiedTime"] = convert_utc_to_local_time(
                task["modifiedTime"], timezone_str,
            )

        # Convert createdTime if present
        if task.get("createdTime"):
            task["createdTime"] = convert_utc_to_local_time(
                task["createdTime"], timezone_str,
            )

    except (ValueError, TypeError) as e:
        logger.debug("Failed to convert task times: %s", e)
        return task
    else:
        return task


def convert_tasks_times_to_local(tasks: list) -> list:
    """
    Convert all time fields in a list of tasks from UTC to local time

    Args:
        tasks: List of task dictionaries

    Returns:
        List of task dictionaries with converted local times
    """
    try:
        converted_tasks = []
        for task in tasks:
            converted_task = convert_task_times_to_local(task)
            converted_tasks.append(converted_task)
    except (ValueError, TypeError) as e:
        logger.debug("Failed to convert tasks times: %s", e)
        return tasks
    else:
        return converted_tasks


def get_user_today(user_timezone: str) -> date:
    """
    Get today's date in user's timezone

    Args:
        user_timezone: User's timezone string like "Asia/Shanghai"

    Returns:
        Today's date in user's timezone
    """
    try:
        if user_timezone and user_timezone.strip():
            tz = pytz.timezone(user_timezone)
            return datetime.now(tz).date()
        # Fallback to UTC if no timezone info
        return datetime.now(timezone.utc).date()
    except pytz.UnknownTimeZoneError as e:
        logger.debug(
            "Failed to get user today with timezone %s: %s", user_timezone, e,
        )
        # Fallback to UTC
        return datetime.now(timezone.utc).date()


def parse_task_date(date_str: str) -> datetime | None:
    """
    Parse task date string to datetime object

    Args:
        date_str: Date string from TickTick API

    Returns:
        Parsed datetime object or None if parsing fails
    """
    if not date_str:
        return None

    try:
        # Handle different date formats from TickTick
        if date_str.endswith("Z"):
            date_str = date_str.replace("Z", "+00:00")
        elif date_str.endswith("+0000"):
            date_str = date_str.replace("+0000", "+00:00")

        return datetime.fromisoformat(date_str)
    except ValueError as e:
        logger.debug("Failed to parse date %s: %s", date_str, e)
        return None


def is_task_due_today(task: dict[str, Any], user_timezone: str) -> bool:
    """
    Check if task is due today in user's timezone

    Args:
        task: Task dictionary
        user_timezone: User's timezone string

    Returns:
        True if task is due today in user's timezone
    """
    try:
        due_date = task.get("dueDate")
        if not due_date:
            return False

        # Parse task due date
        task_datetime = parse_task_date(due_date)
        if not task_datetime:
            return False

        # Get user's today
        user_today = get_user_today(user_timezone)

        # Convert task date to user timezone for comparison
        if user_timezone and user_timezone.strip():
            try:
                tz = pytz.timezone(user_timezone)
                task_local_date = task_datetime.astimezone(tz).date()
            except (pytz.UnknownTimeZoneError, ValueError):
                # If timezone conversion fails, use UTC
                task_local_date = task_datetime.date()
        else:
            task_local_date = task_datetime.date()
        is_due_today = task_local_date == user_today
    except (ValueError, TypeError) as e:
        logger.debug("Failed to check if task is due today: %s", e)
        return False
    else:
        return is_due_today


def is_task_overdue(task: dict[str, Any], user_timezone: str) -> bool:
    """
    Check if task is overdue in user's timezone

    Args:
        task: Task dictionary
        user_timezone: User's timezone string

    Returns:
        True if task is overdue in user's timezone and not completed
    """
    try:
        due_date = task.get("dueDate")
        if not due_date:
            return False

        # Skip completed tasks
        if task.get("status") == COMPLETED_STATUS:
            return False

        # Parse task due date
        task_datetime = parse_task_date(due_date)
        if not task_datetime:
            return False

        # Get user's today
        user_today = get_user_today(user_timezone)

        # Convert task date to user timezone for comparison
        if user_timezone and user_timezone.strip():
            try:
                tz = pytz.timezone(user_timezone)
                task_local_date = task_datetime.astimezone(tz).date()
            except (pytz.UnknownTimeZoneError, ValueError):
                # If timezone conversion fails, use UTC
                task_local_date = task_datetime.date()
        else:
            task_local_date = task_datetime.date()
        is_overdue = task_local_date < user_today
    except (ValueError, TypeError) as e:
        logger.debug("Failed to check if task is overdue: %s", e)
        return False
    else:
        return is_overdue
