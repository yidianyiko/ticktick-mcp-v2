"""
TickTick Client Adapter
Client adapter based on ticktick.py library
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any

from auth import TickTickAuth
from utils.helpers import search_tasks as search_tasks_helper
from utils.timezone_utils import is_task_due_today, is_task_overdue

# Add ticktick.py submodule to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "submodule", "ticktick-py"))

try:
    from ticktick.helpers.time_methods import convert_date_to_tick_tick_format
except ImportError:
    convert_date_to_tick_tick_format = None

logger = logging.getLogger(__name__)


class TickTickAdapter:
    """TickTick client adapter based on ticktick.py library"""

    def __init__(self) -> None:
        """Initialize TickTick adapter"""
        self.auth = TickTickAuth()
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize client"""
        try:
            if self.auth.is_authenticated():
                self.client = self.auth.get_client()
                logger.info("TickTick client initialized successfully")
            else:
                logger.warning("Not authenticated. Please login first.")
        except Exception:
            logger.exception("Failed to initialize client")
            raise

    def _ensure_client(self):
        """Ensure client is initialized"""
        if not self.client:
            self._initialize_client()
        return self.client

    def _get_user_timezone(self) -> str:
        """Get user's timezone from TickTick client"""
        try:
            client = self._ensure_client()
            # ticktick-py library stores user timezone in client.time_zone
            return getattr(client, "time_zone", "")
        except Exception as e:
            logger.debug("Failed to get user timezone: %s", e)
            return ""

    def get_projects(self) -> list[dict[str, Any]]:
        """Get all projects"""
        try:
            client = self._ensure_client()

            # Use ticktick.py library's project manager
            projects = client.state.get("projects", [])

            logger.info("Retrieved %d projects", len(projects))
            return projects

        except Exception:
            logger.exception("Failed to get projects")
            return []

    def get_project(self, project_id: str) -> dict[str, Any] | None:
        """Get specific project details"""
        try:
            client = self._ensure_client()

            # Use ticktick.py library to find project
            projects = client.state.get("projects", [])
            for project in projects:
                if project.get("id") == project_id:
                    return project

            return None

        except Exception:
            logger.exception("Failed to get project %s", project_id)
            return None

    def get_tasks(self, include_completed: bool = False) -> list[dict[str, Any]]:
        """Get all tasks"""
        try:
            client = self._ensure_client()

            # Use ticktick.py library's task manager
            tasks = client.state.get("tasks", [])

            # Filter based on completion status
            if not include_completed:
                tasks = [
                    task for task in tasks if task.get("status") != 2
                ]  # 2 means completed

            logger.info("Retrieved %d tasks", len(tasks))
            return tasks

        except Exception:
            logger.exception("Failed to get tasks")
            return []

    def create_task(
        self, title: str, project_id: str | None = None, **kwargs,
    ) -> dict[str, Any]:
        """Create new task"""
        try:
            client = self._ensure_client()

            # Use ticktick.py library's task manager to create task
            task_data = {"title": title, **kwargs}

            # Only add projectId if provided
            if project_id:
                task_data["projectId"] = project_id

            # Use ticktick.py library's task.builder and task.create
            local_task = client.task.builder(title)
            local_task.update(task_data)

            created_task = client.task.create(local_task)

            logger.info("Created task: %s", title)
            return created_task

        except Exception:
            logger.exception("Failed to create task")
            raise

    def create_task_with_dates(
        self,
        title: str,
        project_id: str | None = None,
        content: str | None = None,
        start_date: datetime | None = None,
        due_date: datetime | None = None,
        priority: int = 0,
        timezone: str = "Asia/Shanghai",
    ) -> dict[str, Any]:
        """Create new task with proper date handling using ticktick.py builder"""
        try:
            client = self._ensure_client()

            # Use ticktick.py's builder method for proper date formatting
            builder_args = {"title": title}

            # Add dates if provided
            if start_date:
                builder_args["startDate"] = start_date
            if due_date:
                builder_args["dueDate"] = due_date
            if timezone:
                builder_args["timeZone"] = timezone
            if project_id:
                builder_args["projectId"] = project_id
            if content:
                builder_args["content"] = content
            if priority:
                builder_args["priority"] = priority

            # Use builder to create properly formatted task
            local_task = client.task.builder(**builder_args)

            # Create the task
            created_task = client.task.create(local_task)

            logger.info("Created task with dates: %s", title)
            return created_task

        except Exception:
            logger.exception("Failed to create task with dates")
            raise

    def update_task(
        self,
        task_id: str,
        project_id: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Update existing task"""
        try:
            client = self._ensure_client()

            # Use ticktick.py library to update task
            # First get task details
            task = client.get_by_id(task_id)
            if not task:
                msg = f"Task {task_id} not found"
                raise Exception(msg)

            # Update task data
            task.update(kwargs)

            # Use ticktick.py library to update task
            updated_task = client.task.update(task)

            logger.info("Updated task: %s", task_id)
            return updated_task

        except Exception:
            logger.exception("Failed to update task %s", task_id)
            raise

    def update_task_with_dates(
        self,
        task_id: str,
        project_id: str | None = None,
        title: str | None = None,
        content: str | None = None,
        start_date: datetime | None = None,
        due_date: datetime | None = None,
        priority: int | None = None,
        timezone: str = "Asia/Shanghai",
    ) -> dict[str, Any]:
        """Update existing task with proper date handling using ticktick.py"""
        try:
            client = self._ensure_client()

            # First get the existing task
            task = client.get_by_id(task_id)
            if not task:
                msg = f"Task {task_id} not found"
                raise Exception(msg)

            # Update basic fields
            if title:
                task["title"] = title
            if content:
                task["content"] = content
            if priority is not None:
                task["priority"] = priority

            # Handle date updates using ticktick.py's date conversion
            if start_date or due_date:
                if convert_date_to_tick_tick_format is None:
                    raise ImportError("ticktick.py library not available")

                if start_date:
                    task["startDate"] = convert_date_to_tick_tick_format(
                        start_date, timezone,
                    )
                if due_date:
                    task["dueDate"] = convert_date_to_tick_tick_format(
                        due_date, timezone,
                    )
                if timezone:
                    task["timeZone"] = timezone

            # Use ticktick.py library to update task
            updated_task = client.task.update(task)

            logger.info("Updated task with dates: %s", task_id)
            return updated_task

        except Exception:
            logger.exception("Failed to update task with dates %s", task_id)
            raise

    def delete_task(self, project_id: str, task_id: str) -> bool:
        """Delete task"""
        try:
            client = self._ensure_client()

            # Create a minimal task object with required fields
            task_obj = {
                "id": task_id,
                "projectId": project_id,
            }

            # Use ticktick.py library to delete task
            client.task.delete(task_obj)

            logger.info("Deleted task: %s from project: %s", task_id, project_id)
            return True  # Return True if no exception occurred

        except Exception:
            logger.exception("Failed to delete task %s", task_id)
            return False

    def complete_task(self, task_id: str) -> bool:
        """Mark task as completed"""
        try:
            client = self._ensure_client()

            # First get the complete task object
            task = client.get_by_id(task_id)
            if not task:
                msg = f"Task {task_id} not found"
                raise Exception(msg)

            # Use ticktick.py library to complete task (needs full task dict)
            client.task.complete(task)

            logger.info("Completed task: %s", task_id)
            return True  # Return True if no exception occurred

        except Exception:
            logger.exception("Failed to complete task %s", task_id)
            raise

    def search_tasks(self, query: str) -> list[dict[str, Any]]:
        """Search tasks by query"""
        try:
            self._ensure_client()

            # Get all tasks first
            all_tasks = self.get_tasks(include_completed=True)

            # Use helper function to search tasks
            tasks = search_tasks_helper(all_tasks, query)

            logger.info("Found %d tasks matching query: %s", len(tasks), query)
            return tasks

        except Exception:
            logger.exception("Failed to search tasks")
            return []

    def get_tasks_by_priority(self, priority: int) -> list[dict[str, Any]]:
        """Get tasks by priority level"""
        try:
            client = self._ensure_client()

            # Get all tasks and filter by priority
            tasks = client.state.get("tasks", [])
            filtered_tasks = [
                task for task in tasks if task.get("priority") == priority
            ]

            logger.info(
                "Found %d tasks with priority %s", len(filtered_tasks), priority,
            )
            return filtered_tasks

        except Exception:
            logger.exception("Failed to get tasks by priority")
            return []

    def get_tasks_due_today(self) -> list[dict[str, Any]]:
        """Get tasks due today in user's timezone"""
        try:
            client = self._ensure_client()

            # Get all tasks and user timezone
            tasks = client.state.get("tasks", [])
            user_timezone = self._get_user_timezone()

            # Filter tasks using timezone-aware comparison
            due_today = []
            for task in tasks:
                if is_task_due_today(task, user_timezone):
                    due_today.append(task)

            logger.info(
                "Found %d tasks due today (timezone: %s)",
                len(due_today),
                user_timezone or "UTC",
            )
            return due_today

        except Exception:
            logger.exception("Failed to get tasks due today")
            return []

    def get_overdue_tasks(self) -> list[dict[str, Any]]:
        """Get overdue tasks in user's timezone"""
        try:
            client = self._ensure_client()

            # Get all tasks and user timezone
            tasks = client.state.get("tasks", [])
            user_timezone = self._get_user_timezone()

            # Filter tasks using timezone-aware comparison
            overdue = []
            for task in tasks:
                if is_task_overdue(task, user_timezone):
                    overdue.append(task)

            logger.info(
                "Found %d overdue tasks (timezone: %s)",
                len(overdue),
                user_timezone or "UTC",
            )
            return overdue

        except Exception:
            logger.exception("Failed to get overdue tasks")
            return []


# Global client instance
_global_client = None


def get_client() -> TickTickAdapter:
    """Get TickTick client instance (singleton pattern)"""
    global _global_client
    if _global_client is None:
        _global_client = TickTickAdapter()
    return _global_client
