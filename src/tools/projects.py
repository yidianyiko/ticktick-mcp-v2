"""
Project Management Tools
Project management MCP tools based on ticktick.py library
"""

import logging
from typing import Any, Dict, List

from adapters.client import get_client
from utils.timezone_utils import convert_tasks_times_to_local

logger = logging.getLogger(__name__)


def get_projects() -> List[Dict[str, Any]]:
    """Get all projects list"""
    try:
        adapter = get_client()
        projects = adapter.get_projects()

        logger.info(f"Retrieved {len(projects)} projects")
        return projects
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        return []


def get_project(project_id: str) -> Dict[str, Any]:
    """Get specific project details"""
    try:
        adapter = get_client()
        project = adapter.get_project(project_id)

        if not project:
            raise Exception(f"Project {project_id} not found")

        logger.info(f"Retrieved project: {project.get('name', 'Unknown')}")
        return project
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {e}")
        raise


def create_project(name: str, color: str = None, view_mode: str = "list") -> Dict[str, Any]:
    """Create new project"""
    try:
        adapter = get_client()
        client = adapter._ensure_client()

        # Use ticktick.py library to create project
        project_data = {"name": name, "view_mode": view_mode}

        if color:
            project_data["color"] = color

        # Use ticktick.py library's project manager to create project
        created_project = client.project.create(name, color if color else None)

        logger.info(f"Created project: {name}")
        return created_project
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise


def delete_project(project_id: str) -> bool:
    """Delete project"""
    try:
        adapter = get_client()
        client = adapter._ensure_client()

        # Use ticktick.py library to delete project
        result = client.project.delete(project_id)

        logger.info(f"Deleted project: {project_id}")
        return result
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {e}")
        raise


def get_project_tasks(project_id: str, include_completed: bool = False) -> List[Dict[str, Any]]:
    """Get tasks in project"""
    try:
        adapter = get_client()
        client = adapter._ensure_client()

        # Get all tasks and filter by project
        all_tasks = client.state.get("tasks", [])
        project_tasks = [task for task in all_tasks if task.get("projectId") == project_id]

        # Filter based on completion status
        if not include_completed:
            project_tasks = [task for task in project_tasks if task.get("status") != 2]

        # Convert UTC times to local times
        project_tasks = convert_tasks_times_to_local(project_tasks)

        logger.info(f"Retrieved {len(project_tasks)} tasks for project {project_id}")
        return project_tasks
    except Exception as e:
        logger.error(f"Error getting project tasks: {e}")
        return []
