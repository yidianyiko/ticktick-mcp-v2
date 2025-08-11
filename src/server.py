#!/usr/bin/env python3
"""
TickTick MCP Server - Simplified Implementation
"""

import asyncio
import logging
import os
import sys
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from auth import TickTickAuth
from tools.auth import AuthTools
from tools.projects import (
    create_project as create_project_impl,
)
from tools.projects import (
    delete_project as delete_project_impl,
)
from tools.projects import (
    get_project as get_project_impl,
)
from tools.projects import (
    get_project_tasks as get_project_tasks_impl,
)

# Import our tools
from tools.projects import (
    get_projects as get_projects_impl,
)
from tools.tasks import (
    complete_task as complete_task_impl,
)
from tools.tasks import (
    create_task as create_task_impl,
)
from tools.tasks import (
    delete_task as delete_task_impl,
)
from tools.tasks import (
    get_overdue_tasks as get_overdue_tasks_impl,
)
from tools.tasks import (
    get_tasks as get_tasks_impl,
)
from tools.tasks import (
    get_tasks_by_priority as get_tasks_by_priority_impl,
)
from tools.tasks import (
    get_tasks_due_today as get_tasks_due_today_impl,
)
from tools.tasks import (
    search_tasks as search_tasks_impl,
)
from tools.tasks import (
    update_task as update_task_impl,
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = FastMCP("ticktick")

# Initialize authentication tools
auth_tools = AuthTools()


# Accepted human-friendly color names mapped to TickTick hex palette.
# This is used to make the API more forgiving for clients.
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


def _is_hex_color(value: str) -> bool:
    """Return True if value is a #RRGGBB hex color string."""
    if not isinstance(value, str):
        return False
    if len(value) != 7 or not value.startswith("#"):
        return False
    hex_part = value[1:]
    try:
        int(hex_part, 16)
        return True
    except ValueError:
        return False


def _normalize_color(color: str | None) -> str | None:
    """Normalize a user-provided color to a TickTick-compatible hex or None.

    - Accepts #RRGGBB directly
    - Accepts common color names (mapped above)
    - Returns None if the input is invalid or empty
    """
    if not color:
        return None
    lowered = color.strip().lower()
    # Direct hex
    if _is_hex_color(lowered):
        return lowered
    # Name mapping
    mapped = COLOR_NAME_TO_HEX.get(lowered)
    if mapped:
        return mapped
    # Unknown value: warn and default to None (let TickTick apply default)
    logger.warning("Unrecognized project color '%s'. Defaulting to TickTick default color.", color)
    return None


# Global client check (similar to reference project)
def ensure_authenticated() -> bool:
    """Ensure client is authenticated, similar to reference project's initialize_client."""
    auth = TickTickAuth()
    if not auth.is_authenticated():
        # Try to authenticate using environment variables if available
        username = os.getenv("TICKTICK_USERNAME")
        password = os.getenv("TICKTICK_PASSWORD")

        if username and password:
            logger.info(
                "Attempting automatic authentication using environment variables",
            )
            if auth.authenticate(username, password):
                logger.info("Automatic authentication successful")
                return True
            logger.warning("Automatic authentication failed")
            return False
        logger.warning("No authentication credentials found")
        return False
    return True


# Helper function to format results
def format_result(data: Any) -> str:
    """Format tool results as readable text."""
    # Add detailed debugging information
    logger.info("format_result received data type: %s", type(data))
    if isinstance(data, list):
        logger.info("format_result received list with %s items", len(data))
        if data and len(data) > 0:
            logger.info("First item type: %s", type(data[0]))
            if isinstance(data[0], dict):
                logger.info("First item keys: %s", list(data[0].keys()))
                logger.info("First item content: %s", data[0])
            else:
                logger.info("First item: %s", data[0])

    if isinstance(data, list):
        if not data:
            return "No items found."

        # Check if this is a list of MCP result format items (with content field)
        if len(data) > 0 and isinstance(data[0], dict) and "content" in data[0]:
            # Handle MCP result format for multiple items
            result = f"Found {len(data)} items:\n\n"
            for i, item in enumerate(data, 1):
                if "content" in item and isinstance(item["content"], list):
                    content = item["content"]
                    if len(content) > 0 and "text" in content[0]:
                        result += f"Item {i}:\n{content[0]['text']}\n\n"
                    else:
                        result += f"Item {i}:\n"
                        for key, value in item.items():
                            if key not in ["content", "type"]:
                                result += f"  {key}: {value}\n"
                        result += "\n"
                else:
                    result += f"Item {i}:\n"
                    for key, value in item.items():
                        if key not in ["content", "type"]:
                            result += f"  {key}: {value}\n"
                    result += "\n"
            return result

        # Format regular list of items (tasks or projects)
        result = f"Found {len(data)} items:\n\n"
        for i, item in enumerate(data, 1):
            if isinstance(item, dict):
                result += f"Item {i}:\n"
                # Log the actual item structure
                logger.info("Processing item %s: %s", i, item)

                # Handle tasks - show key information
                if "title" in item:
                    result += f"  Title: {item.get('title', 'Unknown')}\n"
                    result += f"  ID: {item.get('id', 'Unknown')}\n"
                    result += f"  Project ID: {item.get('projectId', 'Unknown')}\n"
                    result += f"  Priority: {item.get('priority', 0)}\n"
                    result += f"  Status: {item.get('status', 0)}\n"
                    if item.get("dueDate"):
                        result += f"  Due Date: {item.get('dueDate', 'No due date')}\n"
                    if item.get("content"):
                        result += f"  Content: {item.get('content', 'No content')}\n"
                    result += "\n"
                # Handle projects - show key information
                elif "name" in item:
                    result += f"  Name: {item.get('name', 'Unknown')}\n"
                    result += f"  ID: {item.get('id', 'Unknown')}\n"
                    result += f"  Color: {item.get('color', 'Default')}\n"
                    result += f"  View Mode: {item.get('view_mode', 'list')}\n"
                    if item.get("createdTime"):
                        result += f"  Created: {item.get('createdTime', 'Unknown')}\n"
                    result += "\n"
                # Handle other dictionary items
                else:
                    for key, value in item.items():
                        if key not in ["content", "type"]:  # Skip internal fields
                            result += f"  {key}: {value}\n"
                    result += "\n"
            else:
                result += f"{i}. {item}\n"
        return result

    if isinstance(data, dict):
        if "content" in data and isinstance(data["content"], list):
            # Handle MCP result format
            content = data["content"]
            if len(content) > 0 and "text" in content[0]:
                return content[0]["text"]

        # Format dict
        result = ""
        for key, value in data.items():
            if key not in ["content", "type"]:  # Skip internal fields
                result += f"{key}: {value}\n"
        return result

    return str(data)


# Tool definitions
@server.tool()
async def auth_login(username: str, password: str) -> str:
    """Login to TickTick with username and password."""
    try:
        result = await auth_tools.call_tool(
            "auth_login",
            {"username": username, "password": password},
            server,
        )
        return format_result(result)
    except Exception as e:
        logger.exception("Error in auth_login")
        return f"Error: {e!s}"


@server.tool()
async def auth_logout() -> str:
    """Logout from TickTick and clear saved credentials."""
    try:
        result = await auth_tools.call_tool("auth_logout", {}, server)
        return format_result(result)
    except Exception as e:
        logger.exception("Error in auth_logout")
        return f"Error: {e!s}"


@server.tool()
async def auth_status() -> str:
    """Check authentication status."""
    try:
        result = await auth_tools.call_tool("auth_status", {}, server)
        return format_result(result)
    except Exception as e:
        logger.exception("Error in auth_status")
        return f"Error: {e!s}"


# Project Management Tools
@server.tool()
async def get_projects() -> str:
    """Get all projects from TickTick."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        projects = get_projects_impl()
        return format_result(projects)
    except Exception as e:
        logger.exception("Error in get_projects")
        return f"Error retrieving projects: {e!s}"


@server.tool()
async def get_project(project_id: str) -> str:
    """Get details about a specific project."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        project = get_project_impl(project_id)
        return format_result(project)
    except Exception as e:
        logger.exception("Error in get_project")
        return f"Error retrieving project: {e!s}"


@server.tool()
async def create_project(
    name: str, color: str | None = None, view_mode: str = "list",
) -> str:
    """Create a new project.

    Args:
        name: Project name
        color: Optional project color.
            Accepts either a hex color (e.g., "#FF6161") or one of:
            red, pink, teal, green, yellow, purple, blue, mint.
            Unknown values are ignored and TickTick's default color is used.
        view_mode: View mode (not enforced by TickTick API; added to response for convenience)
    """
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        normalized_color = _normalize_color(color)
        project = create_project_impl(name, normalized_color, view_mode)
        return format_result(project)
    except Exception as e:
        logger.exception("Error in create_project")
        return f"Error creating project: {e!s}"


@server.tool()
async def delete_project(project_id: str) -> str:
    """Delete a project."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        result = delete_project_impl(project_id)
        return format_result(result)
    except Exception as e:
        logger.exception("Error in delete_project")
        return f"Error deleting project: {e!s}"


@server.tool()
async def get_project_tasks(project_id: str, include_completed: bool = False) -> str:
    """Get all tasks in a specific project."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        tasks = get_project_tasks_impl(project_id, include_completed)
        return format_result(tasks)
    except Exception as e:
        logger.exception("Error in get_project_tasks")
        return f"Error retrieving project tasks: {e!s}"


# Task Management Tools
@server.tool()
async def get_tasks(include_completed: bool = False) -> str:
    """Get all tasks."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        tasks = get_tasks_impl(include_completed)
        logger.info("get_tasks received %s tasks from get_tasks_impl", len(tasks))
        if tasks and len(tasks) > 0:
            logger.info("First task type: %s", type(tasks[0]))
            if isinstance(tasks[0], dict):
                logger.info("First task keys: %s", list(tasks[0].keys()))
                logger.info("First task title: %s", tasks[0].get("title", "No title"))
        return format_result(tasks)
    except Exception as e:
        logger.exception("Error in get_tasks")
        return f"Error retrieving tasks: {e!s}"


@server.tool()
async def create_task(
    title: str,
    project_id: str | None = None,
    content: str | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
    priority: str = "0",
) -> str:
    """
    Create a new task.

    Args:
        title: Task title/name
        project_id: Optional project ID to place the task in
        content: Optional task description/content
        start_date: Optional start date. Format: "YYYY-MM-DD HH:MM:SS"
            (24-hour, local timezone). Example: "2025-01-01 09:00:00"
        due_date: Optional due date. Format: "YYYY-MM-DD HH:MM:SS"
            (24-hour, local timezone). Example: "2025-01-01 18:00:00"
        priority: Task priority as string
            ("0"=None, "1"=Low, "3"=Medium, "5"=High)

    Examples:
        - Basic task: create_task(title="Buy groceries")
        - Task with dates: create_task(
            title="Meeting", start_date="2024-12-28 14:00:00", due_date="2024-12-28 15:30:00"
        )
        - Task with content: create_task(
            title="Review document", content="Review the quarterly report", priority="3"
        )
    """
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        # Convert priority to int if it's a string (MCP parameter conversion)
        converted_priority = 0
        if isinstance(priority, str):
            try:
                converted_priority = int(priority)
            except ValueError:
                return f"Error: priority must be a valid integer, got '{priority}'"
        else:
            converted_priority = priority

        task = create_task_impl(
            title, project_id, content, start_date, due_date, converted_priority,
        )
        return format_result(task)
    except Exception as e:
        logger.exception("Error in create_task")
        return f"Error creating task: {e!s}"


@server.tool()
async def update_task(
    task_id: str,
    project_id: str | None = None,
    title: str | None = None,
    content: str | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
    priority: str | None = None,
) -> str:
    """
    Update an existing task.

    Args:
        task_id: ID of the task to update
        project_id: Optional new project ID
        title: Optional new task title/name
        content: Optional new task description/content
        start_date: Optional new start date. Format: "YYYY-MM-DD HH:MM:SS"
            (24-hour, local timezone). Example: "2025-01-02 09:00:00"
        due_date: Optional new due date. Format: "YYYY-MM-DD HH:MM:SS"
            (24-hour, local timezone). Example: "2025-01-02 18:00:00"
        priority: Optional new task priority as string
            ("0"=None, "1"=Low, "3"=Medium, "5"=High)

    Examples:
        - Change title: update_task(task_id="12345", title="New task name")
        - Update dates: update_task(
            task_id="12345",
            start_date="2024-12-29 09:00:00",
            due_date="2024-12-29 17:00:00",
        )
        - Change priority: update_task(task_id="12345", priority="5")
    """
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        # Convert priority to int if it's a string (MCP parameter conversion)
        converted_priority = None
        if priority is not None:
            if isinstance(priority, str):
                try:
                    converted_priority = int(priority)
                except ValueError:
                    return f"Error: priority must be a valid integer, got '{priority}'"
            else:
                converted_priority = priority

        task = update_task_impl(
            task_id,
            project_id,
            title,
            content,
            start_date,
            due_date,
            converted_priority,
        )
        return format_result(task)
    except Exception as e:
        logger.exception("Error in update_task")
        return f"Error updating task: {e!s}"


@server.tool()
async def delete_task(task_id: str) -> str:
    """Delete a task by its task_id.

    Args:
        task_id: ID of the task to delete
    """
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        result = delete_task_impl(task_id)
        if isinstance(result, bool):
            return f"Task deletion {'successful' if result else 'failed'}"
        return format_result(result)
    except Exception as e:
        logger.exception("Error in delete_task")
        return f"Error deleting task: {e!s}"


@server.tool()
async def complete_task(task_id: str) -> str:
    """Mark a task as completed."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        result = complete_task_impl(task_id)
        return format_result(result)
    except Exception as e:
        logger.exception("Error in complete_task")
        return f"Error completing task: {e!s}"


@server.tool()
async def search_tasks(query: str) -> str:
    """Search tasks by query."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        tasks = search_tasks_impl(query)
        return format_result(tasks)
    except Exception as e:
        logger.exception("Error in search_tasks")
        return f"Error searching tasks: {e!s}"


@server.tool()
async def get_tasks_by_priority(priority: str) -> str:
    """Get tasks by priority level (0=None, 1=Low, 3=Medium, 5=High)."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        # Convert priority to int if it's a string (MCP parameter conversion)
        converted_priority = 0
        if isinstance(priority, str):
            try:
                converted_priority = int(priority)
            except ValueError:
                return f"Error: priority must be a valid integer, got '{priority}'"
        else:
            converted_priority = priority

        tasks = get_tasks_by_priority_impl(converted_priority)
        return format_result(tasks)
    except Exception as e:
        logger.exception("Error in get_tasks_by_priority")
        return f"Error retrieving tasks by priority: {e!s}"


@server.tool()
async def get_tasks_due_today() -> str:
    """Get tasks due today."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        tasks = get_tasks_due_today_impl()
        return format_result(tasks)
    except Exception as e:
        logger.exception("Error in get_tasks_due_today")
        return f"Error retrieving tasks due today: {e!s}"


@server.tool()
async def get_overdue_tasks() -> str:
    """Get overdue tasks."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        tasks = get_overdue_tasks_impl()
        return format_result(tasks)
    except Exception as e:
        logger.exception("Error in get_overdue_tasks")
        return f"Error retrieving overdue tasks: {e!s}"


async def main() -> None:
    """Main function to run the server."""
    # Check authentication at startup (similar to reference project)
    if not ensure_authenticated():
        logger.warning("Not authenticated. Please use auth_login tool to login.")

    logger.info("Starting TickTick MCP server...")

    # Run the server with FastMCP using stdio transport
    await server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
