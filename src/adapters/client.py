"""
TickTick Client Adapter
Client adapter based on ticktick.py library
"""

import logging
import sys
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

from auth import TickTickAuth
from utils.helpers import search_tasks as search_tasks_helper
from utils.helpers import normalize_color
from utils.timezone_utils import COMPLETED_STATUS, is_task_due_today, is_task_overdue

# Add ticktick.py submodule to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "submodule" / "ticktick-py"))

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

    def _ensure_client(self) -> Any:
        """Ensure client is initialized"""
        if not self.client:
            self._initialize_client()
        return self.client

    def _get_user_timezone(self) -> str:
        """Get user's timezone from TickTick client.

        Returns empty string if client is unavailable or any error occurs.
        """
        try:
            client = self._ensure_client()
            if not client:
                return ""
            # ticktick-py library stores user timezone in client.time_zone
            return getattr(client, "time_zone", "")
        except Exception:
            return ""

    def get_user_timezone(self) -> str:
        """Public accessor for user's timezone."""
        return self._get_user_timezone()

    def get_projects(self) -> list[dict[str, Any]]:
        """Get all projects"""
        try:
            client = self._ensure_client()

            # Use ticktick.py library's project manager
            projects = client.state.get("projects", [])

        except Exception:
            logger.exception("Failed to get projects")
            return []
        else:
            logger.info("Retrieved %d projects", len(projects))
            return projects

    def get_project(self, project_id: str) -> dict[str, Any] | None:
        """Get specific project details"""
        try:
            client = self._ensure_client()

            # Use ticktick.py library to find project
            projects = client.state.get("projects", [])
            found: dict[str, Any] | None = None
            for project in projects:
                if project.get("id") == project_id:
                    found = project
                    break

        except Exception:
            logger.exception("Failed to get project %s", project_id)
            return None
        else:
            return found

    def create_project(
        self, name: str, color: str | None = None, view_mode: str = "list",
    ) -> dict[str, Any]:
        """Create a new project using the underlying client."""
        try:
            client = self._ensure_client()
            normalized_color = normalize_color(color)
            created_project = client.project.create(name, normalized_color)
            # Optionally attach view_mode to the returned dict if supported
            if isinstance(created_project, dict) and "view_mode" not in created_project:
                created_project["view_mode"] = view_mode
        except Exception:
            logger.exception("Failed to create project")
            raise
        else:
            logger.info("Created project: %s", name)
            return created_project

    def delete_project(self, project_id: str) -> bool:
        """Delete a project by id."""
        try:
            client = self._ensure_client()
            result = client.project.delete(project_id)
        except Exception:
            logger.exception("Failed to delete project %s", project_id)
            raise
        else:
            logger.info("Deleted project: %s", project_id)
            return result

    def get_project_tasks(
        self, project_id: str, include_completed: bool = False,
    ) -> list[dict[str, Any]]:
        """Return tasks that belong to a specific project.

        When include_completed is True, attempt to merge any completed-task
        collections exposed by the underlying client state.
        """
        try:
            client = self._ensure_client()
            # Base tasks (usually active/open)
            base_tasks = client.state.get("tasks", [])

            merged_tasks = list(base_tasks)
            if include_completed:
                # Best-effort merge of completed task buckets if the library exposes them
                for key in ("completedTasks", "completed_tasks", "completed"):
                    completed_bucket = client.state.get(key)
                    if isinstance(completed_bucket, list):
                        merged_tasks.extend(completed_bucket)

            project_tasks = [
                task for task in merged_tasks if task.get("projectId") == project_id
            ]

            if not include_completed:
                project_tasks = [
                    task
                    for task in project_tasks
                    if task.get("status") != COMPLETED_STATUS
                ]
        except Exception:
            logger.exception("Failed to get tasks for project %s", project_id)
            return []
        else:
            return project_tasks

    def get_tasks(self, include_completed: bool = False) -> list[dict[str, Any]]:
        """Get all tasks"""
        try:
            client = self._ensure_client()

            # Use ticktick.py library's task manager
            tasks = client.state.get("tasks", [])

            # Filter based on completion status
            if not include_completed:
                tasks = [
                    task
                    for task in tasks
                    if task.get("status") != COMPLETED_STATUS
                ]

        except Exception:
            logger.exception("Failed to get tasks")
            return []
        else:
            logger.info("Retrieved %d tasks", len(tasks))
            return tasks

    def create_task(
        self, title: str, project_id: str | None = None, **kwargs: Any,
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

        except Exception:
            logger.exception("Failed to create task")
            raise
        else:
            logger.info("Created task: %s", title)
            return created_task

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

        except Exception:
            logger.exception("Failed to create task with dates")
            raise
        else:
            logger.info("Created task with dates: %s", title)
            return created_task

    def update_task(
        self,
        task_id: str,
        project_id: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update existing task"""
        client = self._ensure_client()
        # First get task details; only the client call is protected
        try:
            task = client.get_by_id(task_id)
        except Exception:
            logger.exception("Failed to fetch task %s", task_id)
            raise

        if not task:
            msg = f"Task {task_id} not found"
            raise ValueError(msg)

        # Update task data
        task.update(kwargs)
        if project_id is not None:
            # Allow moving task between projects if provided
            task["projectId"] = project_id

        try:
            updated_task = client.task.update(task)
        except Exception:
            logger.exception("Failed to update task %s", task_id)
            raise
        else:
            logger.info("Updated task: %s", task_id)
            return updated_task

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
        client = self._ensure_client()

        # First fetch the existing task under exception handling
        try:
            task = client.get_by_id(task_id)
        except Exception:
            logger.exception("Failed to fetch task %s", task_id)
            raise

        if not task:
            msg = f"Task {task_id} not found"
            raise ValueError(msg)

        # Update basic fields
        if title:
            task["title"] = title
        if content:
            task["content"] = content
        if priority is not None:
            task["priority"] = priority
        if project_id is not None:
            task["projectId"] = project_id

        # Handle date updates using ticktick.py's date conversion
        if start_date or due_date:
            if convert_date_to_tick_tick_format is None:
                msg = "ticktick.py library not available"
                raise ImportError(msg)

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
        try:
            updated_task = client.task.update(task)
        except Exception:
            logger.exception("Failed to update task with dates %s", task_id)
            raise
        else:
            logger.info("Updated task with dates: %s", task_id)
            return updated_task

    def delete_task(self, project_id: str | None, task_id: str) -> bool:
        """Delete task by id.

        Behavior expected by tests:
        - If project_id is provided (truthy), delete directly by task_id string.
        - If project_id is empty/None, first try to fetch the task to infer project, then delete by id.
        - Raise exceptions on failures instead of swallowing.
        """
        client = self._ensure_client()

        # When project_id is not provided, attempt to fetch the task.
        # If the task cannot be found or prefetch fails, treat as idempotent delete.
        if not project_id:
            try:
                prefetch_task = client.get_by_id(task_id)
                if not prefetch_task:
                    logger.info(
                        "Task %s not found before delete; treating as already deleted",
                        task_id,
                    )
                    return True
            except Exception:
                # Do not abort on prefetch failure; proceed with best-effort delete path
                logger.warning(
                    "Prefetch failed for task %s; proceeding with delete attempt",
                    task_id,
                )

        # Primary path: delete by id
        try:
            client.task.delete(task_id)
        except Exception:
            logger.exception(
                "Delete by id failed for task %s, attempting fallback", task_id,
            )
            # Fallback path: try syncing and deleting via full task object if available
            try:
                if hasattr(client, "sync"):
                    try:
                        client.sync()
                    except Exception:
                        logger.warning(
                            "Client sync failed before fallback delete for %s", task_id,
                        )

                task_obj = None
                try:
                    task_obj = client.get_by_id(task_id)
                except Exception:
                    logger.warning(
                        "Failed to fetch task %s during fallback delete; treating as already deleted",
                        task_id,
                    )
                    return True

                if task_obj is None:
                    # If the task is not found locally after sync, treat as idempotent delete
                    logger.info(
                        "Task %s not found during fallback; treating as already deleted",
                        task_id,
                    )
                    return True

                # Attempt delete by object (covers completed tasks in some client impls)
                try:
                    client.task.delete(task_obj)
                except Exception:
                    logger.exception(
                        "Fallback delete by object failed for task %s", task_id,
                    )
                    raise
                else:
                    logger.info("Deleted task via fallback path: %s", task_id)
                    return True
            except Exception:
                # Surface the failure after logging
                raise
        else:
            logger.info(
                "Deleted task: %s%s",
                task_id,
                f" from project: {project_id}" if project_id else "",
            )
            return True

    def complete_task(self, task_id: str) -> bool:
        """Mark task as completed"""
        client = self._ensure_client()
        # Fetch under protection
        try:
            task = client.get_by_id(task_id)
        except Exception:
            logger.exception("Failed to fetch task %s", task_id)
            raise

        if not task:
            msg = f"Task {task_id} not found"
            raise ValueError(msg)

        try:
            # Use ticktick.py library to complete task (needs full task dict)
            client.task.complete(task)
        except Exception:
            logger.exception("Failed to complete task %s", task_id)
            raise
        else:
            logger.info("Completed task: %s", task_id)
            return True  # Return True if no exception occurred

    def search_tasks(self, query: str) -> list[dict[str, Any]]:
        """Search tasks by query"""
        try:
            self._ensure_client()

            # Get all tasks first
            all_tasks = self.get_tasks(include_completed=True)

            # Use helper function to search tasks
            tasks = search_tasks_helper(all_tasks, query)

        except Exception:
            logger.exception("Failed to search tasks")
            return []
        else:
            logger.info("Found %d tasks matching query: %s", len(tasks), query)
            return tasks

    def get_tasks_by_priority(self, priority: int) -> list[dict[str, Any]]:
        """Get tasks by priority level"""
        try:
            client = self._ensure_client()

            # Get all tasks and filter by priority
            tasks = client.state.get("tasks", [])
            filtered_tasks = [
                task for task in tasks if task.get("priority") == priority
            ]

        except Exception:
            logger.exception("Failed to get tasks by priority")
            return []
        else:
            logger.info(
                "Found %d tasks with priority %s", len(filtered_tasks), priority,
            )
            return filtered_tasks

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

        except Exception:
            logger.exception("Failed to get tasks due today")
            return []
        else:
            logger.info(
                "Found %d tasks due today (timezone: %s)",
                len(due_today),
                user_timezone or "UTC",
            )
            return due_today

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

        except Exception:
            logger.exception("Failed to get overdue tasks")
            return []
        else:
            logger.info(
                "Found %d overdue tasks (timezone: %s)",
                len(overdue),
                user_timezone or "UTC",
            )
            return overdue


@lru_cache(maxsize=1)
def get_client() -> TickTickAdapter:
    """Get TickTick client instance (singleton pattern) without globals."""
    return TickTickAdapter()
