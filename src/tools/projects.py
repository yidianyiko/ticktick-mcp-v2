"""
Project Management Tools
Project management MCP tools based on ticktick.py library
"""

import logging
from typing import Any

from adapters.client import get_client
from utils.helpers import normalize_color
from utils.timezone_utils import convert_tasks_times_to_local

logger = logging.getLogger(__name__)


def get_projects() -> list[dict[str, Any]]:
    """Get all projects list"""
    try:
        adapter = get_client()
        projects = adapter.get_projects()
    except Exception:
        logger.exception("Error getting projects")
        return []
    else:
        logger.info("Retrieved %d projects", len(projects))
        return projects


def get_project(project_id: str) -> dict[str, Any]:
    """Get specific project details"""
    try:
        adapter = get_client()
        project = adapter.get_project(project_id)
    except Exception as err:
        logger.exception("Error getting project %s", project_id)
        msg = "Failed to get project"
        raise RuntimeError(msg) from err
    else:
        if not project:
            msg = f"Project {project_id} not found"
            raise ValueError(msg)

        logger.info("Retrieved project: %s", project.get("name", "Unknown"))
        return project


def create_project(
    name: str, color: str | None = None, view_mode: str = "list",
) -> dict[str, Any]:
    """Create new project using client's project manager to match tests"""
    try:
        adapter = get_client()
        client = adapter._ensure_client()

        # If a project with the same name already exists, return it directly
        try:
            existing = next(
                (p for p in adapter.get_projects() if p.get("name") == name),
                None,
            )
        except Exception:
            existing = None
        if existing:
            logger.info("Project already exists with name '%s'; returning existing.", name)
            return existing
        # Normalize color to TickTick-compatible hex or None, with graceful fallback
        normalized_color = normalize_color(color)
        if normalized_color is None:
            created_project = client.project.create(name)
        else:
            try:
                created_project = client.project.create(name, normalized_color)
            except Exception as first_err:  # Retry without color if provider rejects it
                logger.warning(
                    "Project create with color failed; retrying without color. Reason: %s",
                    first_err,
                )
                created_project = client.project.create(name)
    except Exception as err:
        logger.exception("Error creating project")
        msg = f"Failed to create project: {err}"
        raise RuntimeError(msg) from err
    else:
        logger.info("Created project: %s", name)
        return created_project


def delete_project(project_id: str) -> bool:
    """Delete project using client's project manager to match tests"""
    try:
        adapter = get_client()
        client = adapter._ensure_client()
        result = client.project.delete(project_id)
    except Exception as err:
        logger.exception("Error deleting project %s", project_id)
        msg = "Failed to delete project"
        raise RuntimeError(msg) from err
    else:
        logger.info("Deleted project: %s", project_id)
        return result


def get_project_tasks(
    project_id: str, include_completed: bool = False,
) -> list[dict[str, Any]]:
    """Get tasks in project"""
    try:
        adapter = get_client()
        project_tasks = adapter.get_project_tasks(project_id, include_completed)
        # Convert UTC times to local times
        project_tasks = convert_tasks_times_to_local(project_tasks)
    except Exception:
        logger.exception("Error getting project tasks")
        return []
    else:
        logger.info(
            "Retrieved %d tasks for project %s", len(project_tasks), project_id,
        )
        return project_tasks
